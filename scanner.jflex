import java_cup.runtime.*;

%%

%class MyScanner
%cup
%unicode
%line
%column

// Regex definitions
num     = [0-9]+
id      = [_a-zA-Z][_a-zA-Z0-9]*
string  = \"([^\"\n]*)\"

%%

// ---------- Keywords ----------
"store"         { System.out.println("Token: STORE"); return new Symbol(sym.STORE); }
"set"           { System.out.println("Token: SET"); return new Symbol(sym.SET); }
"input"         { System.out.println("Token: INPUT"); return new Symbol(sym.INPUT); }
"into"          { System.out.println("Token: INTO"); return new Symbol(sym.INTO); }
"display"       { System.out.println("Token: DISPLAY"); return new Symbol(sym.DISPLAY); }
"if"            { System.out.println("Token: IF"); return new Symbol(sym.IF); }
"then"          { System.out.println("Token: THEN"); return new Symbol(sym.THEN); }
"otherwise"     { System.out.println("Token: OTHERWISE"); return new Symbol(sym.OTHERWISE); }
"repeat"        { System.out.println("Token: REPEAT"); return new Symbol(sym.REPEAT); }
"times"         { System.out.println("Token: TIMES"); return new Symbol(sym.TIMES); }
"while"         { System.out.println("Token: WHILE"); return new Symbol(sym.WHILE); }
"function"      { System.out.println("Token: FUNCTION"); return new Symbol(sym.FUNCTION); }

// ---------- Operators ----------
">="            { System.out.println("Token: GE (>=)"); return new Symbol(sym.GE); }
"<="            { System.out.println("Token: LE (<=)"); return new Symbol(sym.LE); }
"=="            { System.out.println("Token: EQ (==)"); return new Symbol(sym.EQ); }
"!="            { System.out.println("Token: NE (!=)"); return new Symbol(sym.NE); }
">"             { System.out.println("Token: GT (>)"); return new Symbol(sym.GT); }
"<"             { System.out.println("Token: LT (<)"); return new Symbol(sym.LT); }

"="             { System.out.println("Token: ASSIGN (=)"); return new Symbol(sym.ASSIGN); }
"+"             { System.out.println("Token: PLUS (+)"); return new Symbol(sym.PLUS); }
"-"             { System.out.println("Token: MINUS (-)"); return new Symbol(sym.MINUS); }
"*"             { System.out.println("Token: MULT (*)"); return new Symbol(sym.MULT); }
"/"             { System.out.println("Token: DIV (/)"); return new Symbol(sym.DIV); }

// ---------- Symbols ----------
"("             { System.out.println("Token: LPAREN"); return new Symbol(sym.LPAREN); }
")"             { System.out.println("Token: RPAREN"); return new Symbol(sym.RPAREN); }
"["             { System.out.println("Token: LBRACK"); return new Symbol(sym.LBRACK); }
"]"             { System.out.println("Token: RBRACK"); return new Symbol(sym.RBRACK); }
";"             { System.out.println("Token: SEMI"); return new Symbol(sym.SEMI); }
","             { System.out.println("Token: COMMA"); return new Symbol(sym.COMMA); }

// ---------- Literals ----------
{id}            { System.out.println("Token: ID (" + yytext() + ")"); return new Symbol(sym.ID, yytext()); }
{num}           { System.out.println("Token: NUM (" + yytext() + ")"); return new Symbol(sym.NUM, Integer.valueOf(yytext())); }
{string}        { 
                  String strVal = yytext().substring(1, yytext().length() - 1); 
                  System.out.println("Token: STRING (" + strVal + ")");
                  return new Symbol(sym.STRING, strVal); 
                }

// ---------- Comments ----------
"#".*           { System.out.println("Skipping comment: " + yytext()); }

// ---------- Whitespace ----------
[ \t\r\n]+      { /* skip whitespace */ }

// ---------- Unknown character ----------
.               { System.err.println("Invalid character: " + yytext()); return null; }
