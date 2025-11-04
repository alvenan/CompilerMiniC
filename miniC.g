grammar miniC;

program
    : definition+ ;

definition
    : data_definition
    | function_definition ;

data_definition
    : type_specifier declarator (',' declarator)* ';' ;

type_specifier
    : 'int'
    | 'char'
    ;

declarator
    : IDENTIFIER ;

function_definition
    : type_specifier? function_header function_body ;

function_header
    : declarator parameter_list ;

parameter_list
    : '(' parameter_declaration? ')' ;

parameter_declaration
    : type_specifier declarator (',' declarator)* ;

function_body
    : '{' data_definition* statement* '}' ;

block
    : '{' statement* '}' ;

statement
    : expression ';'
    | 'if' '(' expression ')' statement ('else' statement)?
    | 'while' '(' expression ')' statement
    | 'break' ';'
    | 'continue' ';'
    | 'return' expression? ';'
    | block
    | ';' ;

expression
    : binary ;

binary
    // maior precedência
    : binary '*' binary
    | binary '/' binary
    | binary '%' binary
    | binary '+' binary
    | binary '-' binary
    | binary '<' binary
    | binary '<=' binary
    | binary '>' binary
    | binary '>=' binary
    | binary '==' binary
    | binary '!=' binary
    | IDENTIFIER '=' binary
    | IDENTIFIER '+=' binary
    | IDENTIFIER '-=' binary
    | IDENTIFIER '*=' binary
    | IDENTIFIER '/=' binary
    | IDENTIFIER '%=' binary
    | unary
    ;

unary
    : '++' IDENTIFIER
    | '--' IDENTIFIER
    | primary ;

primary
    : IDENTIFIER
    | CONSTANT_INT
    | CONSTANT_CHAR
    | '(' expression ')'
    | IDENTIFIER '(' argument_list? ')' ;

argument_list
    : binary (',' binary)* ;

IDENTIFIER
    : [a-zA-Z_][a-zA-Z_0-9]* ;

CONSTANT_INT
    : [0-9]+ ;

CONSTANT_CHAR
    : '\'' ( '\\' . | ~['\\] ) '\''
    ;

WS
    : [ \t\r\n]+ -> skip ;