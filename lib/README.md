# Bundled tools

These jars let you build BeginnerScript with only Java installed (no JFlex or CUP setup, no CLASSPATH changes).

| File | Tool | Built from |
|---|---|---|
| `jflex-full-1.9.1.jar` | JFlex 1.9.1 scanner generator (includes the CUP runtime) | [jflex-de/jflex](https://github.com/jflex-de/jflex), release 1.9.1 sources |
| `java-cup-11b.jar` | CUP 0.11b (20160615) parser generator | [DrMichaelPetter/cup](https://github.com/DrMichaelPetter/cup), the official CUP repository |
| `java-cup-11b-runtime.jar` | CUP runtime, needed to compile and run the generated parser | same as above |

Both tools were compiled for Java 11, so any JDK 11 or newer works.
Licences: `LICENSE-JFlex.txt` (BSD-3-Clause) and `LICENSE-CUP.txt` (CUP licence, GPL-compatible).
