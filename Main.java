import java.io.*;
import java.nio.charset.StandardCharsets;
import java_cup.runtime.DefaultSymbolFactory;

/**
 * BeginnerScript compiler driver.
 *
 * Usage: java Main program.txt
 *
 * Exit codes: 0 = no errors, 1 = errors in the program, 2 = bad command line or file.
 */
public class Main {
  @SuppressWarnings("deprecation") // CUP marks its DefaultSymbolFactory deprecated, but it is the right one for plain Symbols
  public static void main(String[] args) {
    if (args.length != 1) {
      System.err.println("Usage: java Main <program-file>");
      System.err.println("Example: java Main input.txt");
      System.exit(2);
    }

    File file = new File(args[0]);
    if (!file.isFile()) {
      System.err.println("File not found: " + args[0]);
      System.exit(2);
    }

    try (Reader in = new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8)) {
      MyScanner scanner = new MyScanner(in);
      parser parser = new parser(scanner, new DefaultSymbolFactory());
      parser.parse();

      int errors = scanner.errors.size() + parser.errors.size();
      if (errors > 0) {
        System.err.println(errors + (errors == 1 ? " error" : " errors") + " found in " + file.getName());
        System.exit(1);
      }
      System.out.println("No errors found in " + file.getName());
    } catch (IOException e) {
      System.err.println("Could not read " + file.getName() + ": " + e.getMessage());
      System.exit(2);
    } catch (Exception e) {
      System.err.println("Internal compiler error: " + e);
      System.exit(1);
    }
  }
}
