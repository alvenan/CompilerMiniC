program 
      : definition { definition } 

definition 
      : data_definition 
      | function_definition 

data_definition 
      : INT declarator { ‘,’ declarator } ‘;‘  

declarator 
      : Identifier 

function_definition 
      : [ INT ] function_header function_body 

function_header 
      : declarator parameter_list 

parameter_list 
      : ‘(‘ [ parameter_declaration ] ‘)‘ 

parameter_declaration 
      : INT declarator { ‘,‘ declarator }  

function_body 
      : ‘{‘ { data_definition } { statement } ‘}‘ 

block 
      : ‘{‘ {statement} ‘}‘  

statement 
      : expression ‘;‘  
      | IF ‘(‘ expression ‘)‘ statement [ ELSE statement ] 
      | WHILE ‘(‘ expression ‘)‘ statement 
      | BREAK ‘;‘ 
      | CONTINUE ‘;‘ 
      | RETURN [ expression ] ‘;‘ 
      | block 
      | ‘;‘ 

expression 
       : binary  

binary 
      : Identifier ‘=‘ binary 
      | Identifier ‘+=‘ binary 
      | Identifier ‘-=‘ binary 
      | Identifier ‘*=‘ binary 
      | Identifier ‘/=‘ binary 
      | Identifier ‘%=‘ binary 
      | binary ‘==‘ binary 
      | binary ‘!=‘ binary 
      | binary ‘<‘ binary 
      | binary ‘<=‘ binary 
      | binary ‘>=‘ binary 
      | binary ‘>=‘ binary 
      | binary ‘+‘ binary 
      | binary ‘-‘ binary 
      | binary ‘*‘ binary 
      | binary ‘/‘ binary 
      | binary ‘%‘ binary 
      | unary 

unary 
      : ‘++‘ Identifier 
      | ‘--‘ Identifier 
      | primary 

primary 
      : IDENTIFIER 
      | CONSTANT_INT 
      | ‘(‘ expression ‘)‘ 
      | Identifier ‘(‘ [ argument_list ] ‘)‘ 

argument_list 
      : binary { ‘,‘ binary }
