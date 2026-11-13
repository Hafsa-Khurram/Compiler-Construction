import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Runs a checked BeginnerScript program by walking its syntax tree.
 *
 * Values are whole numbers (Integer) or text (String). + adds numbers or joins
 * text; - * / work on numbers; comparisons give 1 (true) or 0 (false).
 */
public class Interpreter {
  /** Stops the program with a message that points at the line that failed. */
  public static class RuntimeError extends RuntimeException {
    public RuntimeError(Ast.Node at, String message) {
      super("Runtime error at line " + at.line + ", column " + at.column + ": " + message);
    }
  }

  /** A while loop that runs this many times is treated as an endless loop. */
  static final int MAX_LOOP_RUNS = 100_000;
  /** Function calls nested deeper than this are treated as endless recursion. */
  static final int MAX_CALL_DEPTH = 500;

  private final BufferedReader input;
  private final PrintStream out;
  private final boolean echoInput;
  private final Map<String, Object> globals = new HashMap<>();
  private final Map<String, Ast.Function> functions = new HashMap<>();
  private int callDepth = 0;

  /**
   * @param echoInput print each value read by 'input' after its prompt. Used when the input
   *                  comes from a file or the GUI instead of a person typing in a console.
   */
  public Interpreter(BufferedReader input, PrintStream out, boolean echoInput) {
    this.input = input;
    this.out = out;
    this.echoInput = echoInput;
  }

  public void run(Ast.Program program) {
    for (Ast.Stmt s : program.body) {
      if (s instanceof Ast.Function) functions.put(((Ast.Function) s).name, (Ast.Function) s);
    }
    execBlock(program.body, null);
    out.flush();
  }

  /* ---------------- Statements ---------------- */

  /** @param locals the current function's variables, or null in the main program */
  private void execBlock(List<Ast.Stmt> body, Map<String, Object> locals) {
    for (Ast.Stmt s : body) exec(s, locals);
  }

  private void exec(Ast.Stmt s, Map<String, Object> locals) {
    if (s instanceof Ast.Store) {
      // A stored variable starts as 0 until it is set or read with input
      (locals != null ? locals : globals).put(((Ast.Store) s).name, 0);
    } else if (s instanceof Ast.Set) {
      Ast.Set st = (Ast.Set) s;
      assign(st.name, eval(st.value, locals), locals, st);
    } else if (s instanceof Ast.Input) {
      Ast.Input in = (Ast.Input) s;
      assign(in.name, readInput(in), locals, in);
    } else if (s instanceof Ast.Display) {
      out.println(text(eval(((Ast.Display) s).value, locals)));
    } else if (s instanceof Ast.If) {
      Ast.If st = (Ast.If) s;
      execBlock(isTrue(eval(st.condition, locals)) ? st.thenBody : st.otherwiseBody, locals);
    } else if (s instanceof Ast.While) {
      Ast.While st = (Ast.While) s;
      int runs = 0;
      while (isTrue(eval(st.condition, locals))) {
        if (++runs > MAX_LOOP_RUNS) {
          throw new RuntimeError(st, "this while loop has run " + MAX_LOOP_RUNS
              + " times; does its condition ever become false?");
        }
        execBlock(st.body, locals);
      }
    } else if (s instanceof Ast.Repeat) {
      Ast.Repeat st = (Ast.Repeat) s;
      for (int i = 0; i < st.times; i++) execBlock(st.body, locals);
    } else if (s instanceof Ast.Call) {
      call((Ast.Call) s);
    }
    // Function definitions were registered in run(); they do nothing when reached
  }

  private void call(Ast.Call call) {
    Ast.Function f = functions.get(call.name);
    if (++callDepth > MAX_CALL_DEPTH) {
      throw new RuntimeError(call, "too many nested calls; does '" + call.name + "' keep calling itself?");
    }
    try {
      execBlock(f.body, new HashMap<>());
    } finally {
      callDepth--;
    }
  }

  private Object readInput(Ast.Input in) {
    out.print(in.prompt);
    out.flush();
    String line;
    try {
      line = input.readLine();
    } catch (IOException e) {
      line = null;
    }
    if (line == null) {
      out.println();
      throw new RuntimeError(in, "no input left for '" + in.name + "' (type one value per line in the program input)");
    }
    if (echoInput) out.println(line);
    String value = line.trim();
    if (value.matches("-?\\d{1,10}")) {
      try {
        return Integer.valueOf(value);
      } catch (NumberFormatException e) {
        // too large for a number: keep it as text
      }
    }
    return line;
  }

  /* ---------------- Variables ---------------- */

  private Object lookup(String name, Map<String, Object> locals, Ast.Node at) {
    if (locals != null && locals.containsKey(name)) return locals.get(name);
    if (globals.containsKey(name)) return globals.get(name);
    throw new RuntimeError(at, "variable '" + name + "' has no value yet (its store statement has not run)");
  }

  private void assign(String name, Object value, Map<String, Object> locals, Ast.Node at) {
    if (locals != null && locals.containsKey(name)) locals.put(name, value);
    else if (globals.containsKey(name)) globals.put(name, value);
    else throw new RuntimeError(at, "variable '" + name + "' has no value yet (its store statement has not run)");
  }

  /* ---------------- Expressions ---------------- */

  private Object eval(Ast.Expr e, Map<String, Object> locals) {
    if (e instanceof Ast.Num) return ((Ast.Num) e).value;
    if (e instanceof Ast.Str) return ((Ast.Str) e).value;
    if (e instanceof Ast.Var) return lookup(((Ast.Var) e).name, locals, e);

    Ast.Binary b = (Ast.Binary) e;
    Object left = eval(b.left, locals);
    Object right = eval(b.right, locals);
    try {
      switch (b.op) {
        case "+":
          if (left instanceof String || right instanceof String) return text(left) + text(right);
          return Math.addExact((Integer) left, (Integer) right);
        case "-":
          return Math.subtractExact(number(left, b), number(right, b));
        case "*":
          return Math.multiplyExact(number(left, b), number(right, b));
        case "/": {
          int divisor = number(right, b);
          if (divisor == 0) throw new RuntimeError(b, "division by zero");
          return number(left, b) / divisor; // whole-number division, e.g. 7 / 2 = 3
        }
        case "==":
          return left.equals(right) ? 1 : 0;
        case "!=":
          return left.equals(right) ? 0 : 1;
        case ">":
          return number(left, b) > number(right, b) ? 1 : 0;
        case "<":
          return number(left, b) < number(right, b) ? 1 : 0;
        case ">=":
          return number(left, b) >= number(right, b) ? 1 : 0;
        case "<=":
          return number(left, b) <= number(right, b) ? 1 : 0;
        default:
          throw new RuntimeError(b, "unknown operator " + b.op);
      }
    } catch (ArithmeticException overflow) {
      throw new RuntimeError(b, "the result is too large (numbers go up to 2147483647)");
    }
  }

  private static int number(Object value, Ast.Binary at) {
    if (value instanceof Integer) return (Integer) value;
    throw new RuntimeError(at, "'" + at.op + "' needs numbers, but got the text \"" + value + "\"");
  }

  private static boolean isTrue(Object value) {
    return value instanceof Integer ? (Integer) value != 0 : !((String) value).isEmpty();
  }

  private static String text(Object value) {
    return String.valueOf(value);
  }
}
