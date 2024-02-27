grammar pandaQ;
root : ID ':=' selectStatement ';' #assignacio
     | selectStatement ';' #selectPare
     | 'plot' ID ';' #plotID
     ;


selectStatement : 'select' camps 'from' taula funcionalitats #select
     ;

taula: nomTaula (innerJoin)* #taulaID
     ;

innerJoin:  'inner' 'join' nomTaula 'on' ID '=' ID #taulaInnerJoin
     ;

nomTaula: ID #taulaNom
     ;

funcionalitats: (where) (orderby) #funcionalitatsTaula
     ;

where: (('where' condicio) |) #funcWhere
     ;

orderby: (('order' 'by' campsOrdre) |) #funcOrderby
     ;

camps : (camp ',')* camp #identificadorsCamps
     | '*' #TotsCamps
     ;

condicio : '(' condicio ')' #parentesisCondicio
     | condicio ('and'|'or') condicio #andorCondicio
     | 'not' condicio #notCondicio
     | ID 'in' '(' selectStatement ')' #subquery
     | ID ('<'|'=') Numero #opCondicioID1
     | Numero ('<'|'=') ID #opCondicioID2
     | ID ('<'|'=') ID #opCondicioID3
     ;

campsOrdre: (ID ordreString ',')* ID ordreString #identificadorsCampsOrdre
     ;

ordreString: ('asc'|'desc'|) #ordreCamp
     ;


camp: ID #campSimple
     | calculCamp 'as' ID #campCalculat
     ;

calculCamp: '(' calculCamp ')' #parentesisCamp
     | calculCamp ('*'|'/') calculCamp #opCamp
     | calculCamp ('+'|'-') calculCamp #opCamp
     | ID #idCamp
     | Numero #numeroCamp
     ;

ID : [a-zA-Z_] [a-zA-Z_0-9]*
     ;

Numero : [0-9]+
     ;

WS  : [ \t\n\r]+ -> skip ;