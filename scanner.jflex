import java_cup.runtime.*;

%%

%class MyScanner
%cup
%unicode
%line
%column

%{
  /** A token with its position (0-based line and column, shown +1 in messages). */
  private Symbol symbol(int type) {
    return new Symbol(type, yyline, yycolumn, yytext());
  }

  private Symbol symbol(int type, Object value) {
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
"store"         { System.out.println("Token: STORE"); return symbol(sym.STORE); }
"set"           { System.out.println("Token: SET"); return symbol(sym.SET); }
"input"         { System.out.println("Token: INPUT"); return symbol(sym.INPUT); }
"into"          { System.out.println("Token: INTO"); return symbol(sym.INTO); }
"display"       { System.out.println("Token: DISPLAY"); return symbol(sym.DISPLAY); }
"if"            { System.out.println("Token: IF"); return symbol(sym.IF); }
"then"          { System.out.println("Token: THEN"); return symbol(sym.THEN); }
"otherwise"     { System.out.println("Token: OTHERWISE"); return symbol(sym.OTHERWISE); }
"repeat"        { System.out.println("Token: REPEAT"); return symbol(sym.REPEAT); }
"times"         { System.out.println("Token: TIMES"); return symbol(sym.TIMES); }
"while"         { System.out.println("Token: WHILE"); return symbol(sym.WHILE); }
"function"      { System.out.println("Token: FUNCTION"); return symbol(sym.FUNCTION); }

// ---------- Operators ----------
">="            { System.out.println("Token: GE (>=)"); return symbol(sym.GE); }
"<="            { System.out.println("Token: LE (<=)"); return symbol(sym.LE); }
"=="            { System.out.println("Token: EQ (==)"); return symbol(sym.EQ); }
"!="            { System.out.println("Token: NE (!=)"); return symbol(sym.NE); }
">"             { System.out.println("Token: GT (>)"); return symbol(sym.GT); }
"<"             { System.out.println("Token: LT (<)"); return symbol(sym.LT); }

"="             { System.out.println("Token: ASSIGN (=)"); return symbol(sym.ASSIGN); }
"+"             { System.out.println("Token: PLUS (+)"); return symbol(sym.PLUS); }
"-"             { System.out.println("Token: MINUS (-)"); return symbol(sym.MINUS); }
"*"             { System.out.println("Token: MULT (*)"); return symbol(sym.MULT); }
"/"             { System.out.println("Token: DIV (/)"); return symbol(sym.DIV); }

// ---------- Symbols ----------
"("             { System.out.println("Token: LPAREN"); return symbol(sym.LPAREN); }
")"             { System.out.println("Token: RPAREN"); return symbol(sym.RPAREN); }
"["             { System.out.println("Token: LBRACK"); return symbol(sym.LBRACK); }
"]"             { System.out.println("Token: RBRACK"); return symbol(sym.RBRACK); }
";"             { System.out.println("Token: SEMI"); return symbol(sym.SEMI); }
","             { System.out.println("Token: COMMA"); return symbol(sym.COMMA); }

// ---------- Literals ----------
{id}            { System.out.println("Token: ID (" + yytext() + ")"); return symbol(sym.ID, yytext()); }
{num}           { System.out.println("Token: NUM (" + yytext() + ")"); return symbol(sym.NUM, Integer.valueOf(yytext())); }
{string}        { 
                  String strVal = yytext().substring(1, yytext().length() - 1); 
                  System.out.println("Token: STRING (" + strVal + ")");
                  return symbol(sym.STRING, strVal); 
                }

// ---------- Comments ----------
"#".*           { System.out.println("Skipping comment: " + yytext()); }

// ---------- Whitespace ----------
[ \t\r\n]+      { /* skip whitespace */ }

// ---------- Unknown character ----------
.               { System.err.println("Invalid character: " + yytext()); return null; }
