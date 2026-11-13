import java.io.*;

public class Main {
  public static void main(String argv[]) {
    try {
      MyScanner scanner = new MyScanner(new FileReader(argv[0]));
      parser parser = new parser(scanner);
      Object result = parser.parse();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}