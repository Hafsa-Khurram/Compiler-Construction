import java_cup.runtime.*;

%%

%class MyScanner
%cup
%unicode
%line
%column

%{
  /** Lexical errors found so far (invalid characters, unclosed strings, ...). */
  public final java.util.List<String> errors = new java.util.ArrayList<>();

  private void error(String message) {
    String msg = "Lexical error at line " + (yyline + 1) + ", column " + (yycolumn + 1) + ": " + message;
    errors.add(msg);
    System.err.println(msg);
  }

  /** When true, every token is printed as it is recognised (Main --tokens). */
  public static boolean showTokens = false;

  /** A token with its position (0-based line and column, shown +1 in messages). */
  private Symbol symbol(int type) {
    return symbol(type, yytext());
  }

  private Symbol symbol(int type, Object value) {
    if (showTokens) {
      System.out.printf("%4d:%-4d %-10s %s%n", yyline + 1, yycolumn + 1, sym.terminalNames[type], yytext());
    }
    return new Symbol(type, yyline, yycolumn, value);
  }
%}

%eofval{
  return new Symbol(sym.EOF, yyline, yycolumn);
%eofval}

// Regex definitions
num     = [0-9]+
id      = [_a-zA-Z][_a-zA-Z0-9]*
string  = \"([^\"\n]*)\"

%%

// ---------- Keywords ----------
"store"         { return symbol(sym.STORE); }
"set"           { return symbol(sym.SET); }
"input"         { return symbol(sym.INPUT); }
"into"          { return symbol(sym.INTO); }
"display"       { return symbol(sym.DISPLAY); }
"if"            { return symbol(sym.IF); }
"then"          { return symbol(sym.THEN); }
"otherwise"     { return symbol(sym.OTHERWISE); }
"repeat"        { return symbol(sym.REPEAT); }
"times"         { return symbol(sym.TIMES); }
"while"         { return symbol(sym.WHILE); }
"function"      { return symbol(sym.FUNCTION); }

// ---------- Operators ----------
">="            { return symbol(sym.GE); }
"<="            { return symbol(sym.LE); }
"=="            { return symbol(sym.EQ); }
"!="            { return symbol(sym.NE); }
">"             { return symbol(sym.GT); }
"<"             { return symbol(sym.LT); }

"="             { return symbol(sym.ASSIGN); }
"+"             { return symbol(sym.PLUS); }
"-"             { return symbol(sym.MINUS); }
"*"             { return symbol(sym.MULT); }
"/"             { return symbol(sym.DIV); }

// ---------- Symbols ----------
"("             { return symbol(sym.LPAREN); }
")"             { return symbol(sym.RPAREN); }
"["             { return symbol(sym.LBRACK); }
"]"             { return symbol(sym.RBRACK); }
";"             { return symbol(sym.SEMI); }
","             { return symbol(sym.COMMA); }

// ---------- Literals ----------
{id}            { return symbol(sym.ID, yytext()); }
{num}           {
                  try {
                    return symbol(sym.NUM, Integer.valueOf(yytext()));
                  } catch (NumberFormatException e) {
                    error("number " + yytext() + " is too large (the largest number is 2147483647)");
                    return symbol(sym.NUM, 0);
                  }
                }
{string}        { 
                  return symbol(sym.STRING, yytext().substring(1, yytext().length() - 1));
                }

// A string with no closing quote: report it. The text stops before a ] or ; so that
// a common mistake like  display ["Hello];  does not also hide the rest of the line.
\"[^\"\n\];]*   {
                  error("this string has no closing quote (\")");
                  return symbol(sym.STRING, yytext().substring(1));
                }

// ---------- Comments ----------
"#".*           { /* skip comments */ }

// ---------- Whitespace ----------
[ \t\r\n]+      { /* skip whitespace */ }

// ---------- Unknown character ----------
// Report it and carry on scanning (returning null here used to crash the parser)
[^]             { error("invalid character '" + yytext() + "'"); }
