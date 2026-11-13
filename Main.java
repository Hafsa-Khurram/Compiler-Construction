import java.io.*;
import java.nio.charset.StandardCharsets;
import java_cup.runtime.DefaultSymbolFactory;

/**
 * BeginnerScript compiler driver.
 *
 * Phases: lexical analysis (MyScanner, from scanner.jflex), syntax analysis
 * (parser, from parser.cup, builds an Ast), semantic analysis (Semantic) and
 * execution (Interpreter). The program only runs if no errors were found.
 *
 * Usage: java Main [--tokens] [--tree] [--check] program.txt
 *
 *   --tokens print every token found by the scanner
 *   --tree   print the abstract syntax tree built by the parser
 *   --check  stop after semantic analysis (do not run the program)
 *
 * Exit codes: 0 = ok, 1 = errors in the program, 2 = bad command line or file,
 * 3 = runtime error while the program was running.
 */
public class Main {
  @SuppressWarnings("deprecation") // CUP marks its DefaultSymbolFactory deprecated, but it is the right one for plain Symbols
  public static void main(String[] args) {
    boolean showTokens = false;
    boolean showTree = false;
    boolean checkOnly = false;
    String path = null;
    for (String arg : args) {
      if (arg.equals("--tokens")) showTokens = true;
      else if (arg.equals("--tree")) showTree = true;
      else if (arg.equals("--check")) checkOnly = true;
      else if (arg.startsWith("--") || path != null) usage("Unknown option: " + arg);
      else path = arg;
    }
    if (path == null) usage(null);

    File file = new File(path);
    if (!file.isFile()) {
      System.err.println("File not found: " + path);
      System.exit(2);
    }

    try (Reader in = new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8)) {
      MyScanner.showTokens = showTokens;
      if (showTokens) {
        System.out.println("=== Tokens ===");
        System.out.println("line:col  token      text");
      }
      MyScanner scanner = new MyScanner(in);
      parser parser = new parser(scanner, new DefaultSymbolFactory());
      java_cup.runtime.Symbol result = parser.parse();

      int errors = scanner.errors.size() + parser.errors.size();
      if (errors > 0) {
        System.err.println(errors + (errors == 1 ? " error" : " errors") + " found in " + file.getName());
        System.exit(1);
      }
      // Only use the tree when parsing succeeded (after errors the result is incomplete)
      Ast.Program program = (Ast.Program) result.value;

      // Semantic analysis: names, scopes and simple type checks
      Semantic semantic = new Semantic();
      semantic.check(program);
      for (String error : semantic.errors) System.err.println(error);
      if (!semantic.errors.isEmpty()) {
        int n = semantic.errors.size();
        System.err.println(n + (n == 1 ? " error" : " errors") + " found in " + file.getName());
        System.exit(1);
      }
      if (showTree) {
        System.out.println("=== Syntax tree ===");
        System.out.print(Ast.toTree(program));
      }
      if (checkOnly) {
        System.out.println("No errors found in " + file.getName());
        return;
      }

      // Execution
      if (showTokens || showTree) System.out.println("=== Program output ===");
      System.out.flush();
      BufferedReader stdin = new BufferedReader(new InputStreamReader(System.in));
      boolean typedByPerson = System.console() != null;
      try {
        new Interpreter(stdin, System.out, !typedByPerson).run(program);
      } catch (Interpreter.RuntimeError e) {
        System.out.flush();
        System.err.println(e.getMessage());
        System.exit(3);
      }
    } catch (IOException e) {
      System.err.println("Could not read " + file.getName() + ": " + e.getMessage());
      System.exit(2);
    } catch (Exception e) {
      System.err.println("Internal compiler error: " + e);
      System.exit(1);
    }
  }

  private static void usage(String problem) {
    if (problem != null) System.err.println(problem);
    System.err.println("Usage: java Main [--tokens] [--tree] [--check] <program-file>");
    System.err.println("Example: java Main examples/input.txt");
    System.exit(2);
  }
}
