import java.util.ArrayList;
import java.util.List;

/**
 * Abstract syntax tree (AST) for BeginnerScript.
 *
 * The parser (parser.cup) builds these nodes. Semantic analysis and execution
 * then walk the tree, so a program is checked completely before any of it runs.
 */
public final class Ast {
  private Ast() {
  }

  /** Every node remembers where it starts in the source (1-based line and column). */
  public abstract static class Node {
    public final int line;
    public final int column;

    Node(int line, int column) {
      this.line = line;
      this.column = column;
    }

    /** Text shown for this node in the syntax tree, e.g. "Set age". */
    public abstract String label();

    /** Nodes shown under this one in the syntax tree. */
    public List<Node> children() {
      return List.of();
    }
  }

  public abstract static class Stmt extends Node {
    Stmt(int line, int column) {
      super(line, column);
    }
  }

  public abstract static class Expr extends Node {
    Expr(int line, int column) {
      super(line, column);
    }
  }

  /* ---------------- Program ---------------- */

  public static final class Program extends Node {
    public final List<Stmt> body;

    public Program(List<Stmt> body) {
      super(1, 1);
      this.body = body;
    }

    public String label() {
      return "Program";
    }

    public List<Node> children() {
      return new ArrayList<>(body);
    }
  }

  /** A labelled group of statements, only used to show if/while bodies in the tree. */
  static final class Group extends Node {
    final String name;
    final List<? extends Node> items;

    Group(String name, List<? extends Node> items) {
      super(0, 0);
      this.name = name;
      this.items = items;
    }

    public String label() {
      return items.isEmpty() ? name + " (empty)" : name;
    }

    public List<Node> children() {
      return new ArrayList<>(items);
    }
  }

  /* ---------------- Statements ---------------- */

  /** store name; */
  public static final class Store extends Stmt {
    public final String name;

    public Store(int line, int column, String name) {
      super(line, column);
      this.name = name;
    }

    public String label() {
      return "Store " + name;
    }
  }

  /** set name = value; */
  public static final class Set extends Stmt {
    public final String name;
    public final Expr value;

    public Set(int line, int column, String name, Expr value) {
      super(line, column);
      this.name = name;
      this.value = value;
    }

    public String label() {
      return "Set " + name;
    }

    public List<Node> children() {
      return List.of(value);
    }
  }

  /** input "prompt" into name; */
  public static final class Input extends Stmt {
    public final String prompt;
    public final String name;

    public Input(int line, int column, String prompt, String name) {
      super(line, column);
      this.prompt = prompt;
      this.name = name;
    }

    public String label() {
      return "Input \"" + prompt + "\" into " + name;
    }
  }

  /** display [value]; */
  public static final class Display extends Stmt {
    public final Expr value;

    public Display(int line, int column, Expr value) {
      super(line, column);
      this.value = value;
    }

    public String label() {
      return "Display";
    }

    public List<Node> children() {
      return List.of(value);
    }
  }

  /** if condition then [ ... ] otherwise [ ... ] */
  public static final class If extends Stmt {
    public final Expr condition;
    public final List<Stmt> thenBody;
    public final List<Stmt> otherwiseBody;

    public If(int line, int column, Expr condition, List<Stmt> thenBody, List<Stmt> otherwiseBody) {
      super(line, column);
      this.condition = condition;
      this.thenBody = thenBody;
      this.otherwiseBody = otherwiseBody;
    }

    public String label() {
      return "If";
    }

    public List<Node> children() {
      return List.of(condition, new Group("then", thenBody), new Group("otherwise", otherwiseBody));
    }
  }

  /** while condition [ ... ] */
  public static final class While extends Stmt {
    public final Expr condition;
    public final List<Stmt> body;

    public While(int line, int column, Expr condition, List<Stmt> body) {
      super(line, column);
      this.condition = condition;
      this.body = body;
    }

    public String label() {
      return "While";
    }

    public List<Node> children() {
      return List.of(condition, new Group("do", body));
    }
  }

  /** repeat N times [ ... ] */
  public static final class Repeat extends Stmt {
    public final int times;
    public final List<Stmt> body;

    public Repeat(int line, int column, int times, List<Stmt> body) {
      super(line, column);
      this.times = times;
      this.body = body;
    }

    public String label() {
      return "Repeat " + times + " times";
    }

    public List<Node> children() {
      return new ArrayList<>(body);
    }
  }

  /** function name(param, ...) [ ... ] */
  public static final class Function extends Stmt {
    public final String name;
    public final List<String> params;
    public final List<Stmt> body;

    public Function(int line, int column, String name, List<String> params, List<Stmt> body) {
      super(line, column);
      this.name = name;
      this.params = params;
      this.body = body;
    }

    public String label() {
      return "Function " + name + "(" + String.join(", ", params) + ")";
    }

    public List<Node> children() {
      return new ArrayList<>(body);
    }
  }

  /** name(argument, ...); */
  public static final class Call extends Stmt {
    public final String name;
    public final List<Expr> args;

    public Call(int line, int column, String name, List<Expr> args) {
      super(line, column);
      this.name = name;
      this.args = args;
    }

    public String label() {
      return "Call " + name + "()" + (args.isEmpty() ? "" : " with " + args.size() + (args.size() == 1 ? " argument" : " arguments"));
    }

    public List<Node> children() {
      return new ArrayList<>(args);
    }
  }

  /* ---------------- Expressions ---------------- */

  /** left op right, where op is one of + - * / > < >= <= == != */
  public static final class Binary extends Expr {
    public final String op;
    public final Expr left;
    public final Expr right;

    public Binary(int line, int column, String op, Expr left, Expr right) {
      super(line, column);
      this.op = op;
      this.left = left;
      this.right = right;
    }

    public String label() {
      return op;
    }

    public List<Node> children() {
      return List.of(left, right);
    }
  }

  public static final class Var extends Expr {
    public final String name;

    public Var(int line, int column, String name) {
      super(line, column);
      this.name = name;
    }

    public String label() {
      return "Variable " + name;
    }
  }

  public static final class Num extends Expr {
    public final int value;

    public Num(int line, int column, int value) {
      super(line, column);
      this.value = value;
    }

    public String label() {
      return "Number " + value;
    }
  }

  public static final class Str extends Expr {
    public final String value;

    public Str(int line, int column, String value) {
      super(line, column);
      this.value = value;
    }

    public String label() {
      return "Text \"" + value + "\"";
    }
  }

  /* ---------------- Printing ---------------- */

  /** The tree as indented text (ASCII only, so it shows correctly in any console). */
  public static String toTree(Node root) {
    StringBuilder out = new StringBuilder(root.label()).append('\n');
    appendChildren(root, "", out);
    return out.toString();
  }

  private static void appendChildren(Node node, String indent, StringBuilder out) {
    List<Node> kids = node.children();
    for (int i = 0; i < kids.size(); i++) {
      boolean last = i == kids.size() - 1;
      Node kid = kids.get(i);
      out.append(indent).append(last ? "`-- " : "+-- ").append(kid.label()).append('\n');
      appendChildren(kid, indent + (last ? "    " : "|   "), out);
    }
  }
}
