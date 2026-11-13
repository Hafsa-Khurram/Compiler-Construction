import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Semantic analysis for BeginnerScript.
 *
 * Runs after parsing and before the program is executed. It checks that
 *  - variables are stored (declared) before they are used, and only once per scope,
 *  - called functions exist, are defined once, and only at the top level,
 *  - text is not used with - * / or with < > <= >=, and nothing is divided by 0.
 *
 * Scopes: the main program has one global scope (blocks share it). Each function
 * has its own local scope and can also use any global variable.
 */
public class Semantic {
  /** Semantic errors found, sorted by line and column. */
  public final List<String> errors = new ArrayList<>();

  /** Errors as they are found (the function pass runs first, so they are sorted afterwards). */
  private final List<Ast.Node> errorNodes = new ArrayList<>();
  private final List<String> errorTexts = new ArrayList<>();

  private final Map<String, Ast.Function> functions = new LinkedHashMap<>();

  /** A scope maps variable names to the node that stored them. */
  private static final class Scope {
    final Scope parent;
    final Map<String, Ast.Node> names = new HashMap<>();

    Scope(Scope parent) {
      this.parent = parent;
    }

    Ast.Node find(String name) {
      for (Scope s = this; s != null; s = s.parent) {
        Ast.Node node = s.names.get(name);
        if (node != null) return node;
      }
      return null;
    }

    /** All names visible from this scope (for "did you mean" hints). */
    List<String> visible() {
      List<String> all = new ArrayList<>();
      for (Scope s = this; s != null; s = s.parent) all.addAll(s.names.keySet());
      return all;
    }
  }

  /** Every variable stored anywhere in the main program; function bodies may use them. */
  private final Scope allGlobals = new Scope(null);

  public void check(Ast.Program program) {
    // Pass 1: find every function, so a function can be called before its definition
    for (Ast.Stmt s : program.body) {
      if (s instanceof Ast.Function) {
        Ast.Function f = (Ast.Function) s;
        Ast.Function earlier = functions.get(f.name);
        if (earlier != null) {
          error(f, "function '" + f.name + "' is already defined at line " + earlier.line);
        } else {
          functions.put(f.name, f);
        }
      }
    }
    collectGlobals(program.body);

    // Pass 2: check the statements in order
    checkBlock(program.body, new Scope(null), true);

    List<Integer> order = new ArrayList<>();
    for (int i = 0; i < errorNodes.size(); i++) order.add(i);
    order.sort((a, b) -> errorNodes.get(a).line != errorNodes.get(b).line
        ? Integer.compare(errorNodes.get(a).line, errorNodes.get(b).line)
        : Integer.compare(errorNodes.get(a).column, errorNodes.get(b).column));
    for (int i : order) errors.add(errorTexts.get(i));
  }

  private void collectGlobals(List<Ast.Stmt> body) {
    for (Ast.Stmt s : body) {
      if (s instanceof Ast.Store) allGlobals.names.putIfAbsent(((Ast.Store) s).name, s);
      else if (s instanceof Ast.If) {
        collectGlobals(((Ast.If) s).thenBody);
        collectGlobals(((Ast.If) s).otherwiseBody);
      } else if (s instanceof Ast.While) collectGlobals(((Ast.While) s).body);
      else if (s instanceof Ast.Repeat) collectGlobals(((Ast.Repeat) s).body);
    }
  }

  private void checkBlock(List<Ast.Stmt> body, Scope scope, boolean topLevel) {
    for (Ast.Stmt s : body) checkStmt(s, scope, topLevel);
  }

  private void checkStmt(Ast.Stmt s, Scope scope, boolean topLevel) {
    if (s instanceof Ast.Store) {
      Ast.Store st = (Ast.Store) s;
      Ast.Node earlier = scope.names.get(st.name);
      if (earlier != null) {
        error(st, "variable '" + st.name + "' is already stored at line " + earlier.line);
      } else {
        scope.names.put(st.name, st);
      }
    } else if (s instanceof Ast.Set) {
      Ast.Set st = (Ast.Set) s;
      checkExpr(st.value, scope);
      requireVariable(st.name, st, scope);
    } else if (s instanceof Ast.Input) {
      Ast.Input in = (Ast.Input) s;
      requireVariable(in.name, in, scope);
    } else if (s instanceof Ast.Display) {
      checkExpr(((Ast.Display) s).value, scope);
    } else if (s instanceof Ast.If) {
      Ast.If st = (Ast.If) s;
      checkExpr(st.condition, scope);
      checkBlock(st.thenBody, scope, false);
      checkBlock(st.otherwiseBody, scope, false);
    } else if (s instanceof Ast.While) {
      Ast.While st = (Ast.While) s;
      checkExpr(st.condition, scope);
      checkBlock(st.body, scope, false);
    } else if (s instanceof Ast.Repeat) {
      checkBlock(((Ast.Repeat) s).body, scope, false);
    } else if (s instanceof Ast.Function) {
      Ast.Function f = (Ast.Function) s;
      if (!topLevel) {
        error(f, "function '" + f.name + "' must be defined at the top level of the program, not inside a block");
      }
      // Parameters are local variables of the function
      Scope local = new Scope(allGlobals);
      for (String p : f.params) {
        if (local.names.containsKey(p)) error(f, "function '" + f.name + "' has two parameters called '" + p + "'");
        local.names.put(p, f);
      }
      checkBlock(f.body, local, false);
    } else if (s instanceof Ast.Call) {
      Ast.Call call = (Ast.Call) s;
      for (Ast.Expr arg : call.args) checkExpr(arg, scope);
      Ast.Function f = functions.get(call.name);
      if (f == null) {
        error(call, "function '" + call.name + "' is not defined" + suggestion(call.name, new ArrayList<>(functions.keySet())));
      } else if (f.params.size() != call.args.size()) {
        error(call, "function '" + call.name + "' needs " + count(f.params.size(), "argument")
            + " but was given " + call.args.size());
      }
    }
  }

  private void requireVariable(String name, Ast.Node at, Scope scope) {
    if (scope.find(name) == null) {
      error(at, "variable '" + name + "' is used before it is stored (add: store " + name + ";)"
          + suggestion(name, scope.visible()));
    }
  }

  /* ---------------- Expressions and simple type checks ---------------- */

  private enum Type { NUMBER, TEXT, UNKNOWN }

  private Type checkExpr(Ast.Expr e, Scope scope) {
    if (e instanceof Ast.Num) return Type.NUMBER;
    if (e instanceof Ast.Str) return Type.TEXT;
    if (e instanceof Ast.Var) {
      requireVariable(((Ast.Var) e).name, e, scope);
      return Type.UNKNOWN; // a variable can hold a number or text
    }
    Ast.Binary b = (Ast.Binary) e;
    Type left = checkExpr(b.left, scope);
    Type right = checkExpr(b.right, scope);
    switch (b.op) {
      case "+":
        if (left == Type.TEXT || right == Type.TEXT) return Type.TEXT;
        return left == Type.NUMBER && right == Type.NUMBER ? Type.NUMBER : Type.UNKNOWN;
      case "-":
      case "*":
      case "/":
        if (left == Type.TEXT || right == Type.TEXT) {
          error(b, "'" + b.op + "' only works with numbers (use + to join text)");
        }
        if (b.op.equals("/") && b.right instanceof Ast.Num && ((Ast.Num) b.right).value == 0) {
          error(b, "division by zero");
        }
        return Type.NUMBER;
      case "==":
      case "!=":
        return Type.NUMBER;
      default: // > < >= <=
        if (left == Type.TEXT || right == Type.TEXT) {
          error(b, "'" + b.op + "' only compares numbers (use == or != for text)");
        }
        return Type.NUMBER;
    }
  }

  /* ---------------- Helpers ---------------- */

  private void error(Ast.Node at, String message) {
    errorNodes.add(at);
    errorTexts.add("Semantic error at line " + at.line + ", column " + at.column + ": " + message);
  }

  private static String count(int n, String word) {
    return n + " " + word + (n == 1 ? "" : "s");
  }

  /** " (did you mean 'welcome'?)" when a known name differs only in upper/lower case. */
  private static String suggestion(String name, List<String> known) {
    for (String k : known) {
      if (k.equalsIgnoreCase(name)) return " (did you mean '" + k + "'?)";
    }
    return "";
  }
}
