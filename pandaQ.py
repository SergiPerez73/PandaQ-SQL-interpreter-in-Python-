from pandaQVisitor import pandaQVisitor
import pandas as pd
import streamlit as st
from antlr4 import *
from pandaQLexer import pandaQLexer
from pandaQParser import pandaQParser


class pandaQ(pandaQVisitor):

    # Funcio que carrega la sessio per tenir aquelles taules desades
    def __init__(self):
        # Comprovem si la sessio es buida. Com desem la taula de simbols a 'key',
        # si 'key' no hi es, la sessio es buida.
        if 'key' not in st.session_state:
            # Inicialitzem la sessio i enllacem la taula de simbols amb la
            # posicio 'key' de la sessio.
            st.session_state['key'] = {}
            self.ts = st.session_state['key']
        else:
            # Enllacem la taula de simbols amb la posicio 'key' de la sessio. On hi sera allo que
            # haguem desat previament.
            self.ts = st.session_state['key']

    # Funcio que visita el pare del Select.
    def visitSelectPare(self, ctx):
        [selectStatement, _] = list(ctx.getChildren())
        self.visit(selectStatement)
        # Mostrem la taula self.df amb el Streamlit.
        st.table(self.df)

    # Funcio que visita l'assignacio d'una taula a un simbol.
    def visitAssignacio(self, ctx):
        [clau, _, selectStatement, _] = list(ctx.getChildren())

        self.visit(selectStatement)
        # Assignem a la clau determinada la taula self.df a la taula self.ts
        self.ts[clau.getText()] = self.df
        st.table(self.df)

    # Funcio que visita el graficar d'una taula desada a la taula de simbols.
    def visitPlotID(self, ctx):
        [_, variable, _] = list(ctx.getChildren())
        if (variable.getText() in self.ts):
            # Agafem nomes els camps numerics de la taula
            df_num = self.ts[variable.getText()].select_dtypes(
                include=['int', 'float'])
            # Fem plot de la taula amb la funcio de Streamlit line_chart
            st.line_chart(df_num)

    # Funcio que visita el select.
    def visitSelect(self, ctx):
        [_, campsIdent, _, taula, funcionalitats] = list(ctx.getChildren())
        # Visitem la taula, que es desara a self.df
        self.visit(taula)
        # Desem els camps que s'hagin mostrar. Sera buit si volem mostrat tot.
        camps = self.visit(campsIdent)
        # Visitem les funcionalitats extres que s'hagin d'afegir, com order by
        # o where.
        self.visit(funcionalitats)
        # Si no es buit es tracta d'un select amb camps especifics a consultar,
        # no un select all.
        if (len(camps) > 0):
            # Ens quedem nomes amb les columnes demanades.
            self.df = self.df[camps]

    # Funcio que visita la taula que es selecciona.
    def visitTaulaID(self, ctx):
        L = list(ctx.getChildren())
        # A la primera possicio trobem el nom de la taula.
        taula = list(ctx.getChildren())[0]
        # Aquesta taula s'assigna a self.df
        self.df = self.visit(taula)

        # Visitem els inner joins que hi hagi.
        for i in L[1:]:
            self.visit(i)

    # Funcio que visita un inner join
    def visitTaulaInnerJoin(self, ctx):
        Children = list(ctx.getChildren())

        if (len(Children) > 0):
            [_, _, taula2, _, camp1, _, camp2] = Children
            # Es visita la taula amb la que es fa l'inner join i s'assigna a
            # df2
            df2 = self.visit(taula2)

            # Es fa el corresponent merge a self.df.
            self.df = self.df.merge(
                df2,
                left_on=camp1.getText(),
                right_on=camp2.getText(),
                how="inner")

    # Funcio que visita una taula, nomes amb el seu nom
    def visitTaulaNom(self, ctx):
        [taula] = list(ctx.getChildren())

        # Si la taula ja es a la taula de simbols, es retorna aquesta
        if (taula.getText() in self.ts):
            return self.ts[taula.getText()]
        # Si la taula no es a la taula de simbols, ha de ser com a arxiu .csv.
        else:
            nomArxiu = taula.getText() + '.csv'
            df = pd.read_csv(nomArxiu)
            return df

    # Funcio que visita les funcionalitats de taula.
    def visitFuncionalitatsTaula(self, ctx):
        [funcWhere, funcOrderby] = list(ctx.getChildren())

        # Es visiten els possibles where i order by
        self.visit(funcWhere)
        self.visit(funcOrderby)

    # Funcio que visita el where
    def visitFuncWhere(self, ctx):
        Children = list(ctx.getChildren())

        # Si Children no es buit, es canvia el self.df, deixant nomes les files
        # que compleixen la condicio.
        if (len(Children) > 0):
            [_, condicio] = Children
            self.df = self.df[self.visit(condicio)]

    # Funcio que visita l'order by.
    def visitFuncOrderby(self, ctx):
        Children = list(ctx.getChildren())

        # S'ordena en funcio de determinats camps, si no es buit Children.
        if (len(Children) > 0):
            [_, _, campsOrdre] = Children
            self.visit(campsOrdre)

    # Funcio que visita els camps que indicaran l'ordre de la taula self.df.
    def visitIdentificadorsCampsOrdre(self, ctx):
        childrenL = list(ctx.getChildren())  # Desem tots els fills.

        # En les posicions multiples de 3, es troben els ids dels camps.
        campsFills = list(childrenL)[0::3]
        camps = []
        # Recorrem campsFills i afegim els camps amb getText.
        for i in campsFills:
            camps.append(i.getText())

        # En les posicions multiples de 3 mes 1, es troba si
        # es tracta d'ordre ascendent o descendent.
        ascFills = list(childrenL)[1::3]
        asc = []

        # Recorrem ascFills i afegim TRUE si es acendent i FALSE si no visitant
        # cadascun.
        for i in ascFills:
            asc.append((self.visit(i) == 'asc'))

        # Una vegada tenim els camps i l'ordre, ordenem self.df.
        self.df = self.df.sort_values(by=camps, ascending=asc)

    # Funcio que visita l'ordre d'un camp, que pot ser ascendent o descendent.
    def visitOrdreCamp(self, ctx):
        childrenL = list(ctx.getChildren())
        if (len(childrenL) == 0):  # Si es buit, considerem que es ascendent.
            return 'asc'
        else:  # Si no es buit, retornem el text introduit.
            [ordre] = childrenL
            return ordre.getText()

    # Funcio que visita els identificadors els camps.
    def visitIdentificadorsCamps(self, ctx):
        # Els camps es troben a les posicions parelles.
        campsFills = list(ctx.getChildren())[0::2]

        camps = []
        # Llegim el text dels camps i ho retornem.
        for i in campsFills:
            camps.append(self.visit(i))

        return camps

    # Funcio que visita el cas en que es visita tots els camps.
    def visitTotsCamps(self, ctx):
        camps = []
        # En aquest cas, retornem una llista buida.
        return camps

    # Funcio que visita un camp no calculat.
    def visitCampSimple(self, ctx):
        # Desem el camp i retornem el seu text.
        [idCamp] = list(ctx.getChildren())
        return (idCamp.getText())

    # Funcio que visita un camp calculat.
    def visitCampCalculat(self, ctx):
        # Desem l'expressio del calcul i l'id del nou camp.
        [calculCamp, _, idCamp] = list(ctx.getChildren())
        # Creem un nou camp amb el resultat de l'expressio a self.df.
        self.df[idCamp.getText()] = self.visit(calculCamp)
        return (idCamp.getText())  # Retornem l'id del nou camp.

    # Funcio que visita una operacio a una expressio d'un camp calculat.
    def visitOpCamp(self, ctx):
        # Desem les dues expressions i l'operador.
        [calculCamp1, operador, calculCamp2] = list(ctx.getChildren())

        # Apliquem l'operador pertinent en cada cas.
        if (operador.getText() == '+'):
            return self.visit(calculCamp1) + self.visit(calculCamp2)
        elif (operador.getText() == '-'):
            return self.visit(calculCamp1) - self.visit(calculCamp2)
        elif (operador.getText() == '*'):
            return self.visit(calculCamp1) * self.visit(calculCamp2)
        elif (operador.getText() == '/'):
            return self.visit(calculCamp1) / self.visit(calculCamp2)

    # Funcio que visita un parantesis a una expressio d'un camp calculat.
    def visitParentesisCamp(self, ctx):
        # Llegim l'expressio.
        [_, calculCamp, _] = list(ctx.getChildren())

        # Retornem l'expressio.
        return (self.visit(calculCamp))

    # Funcio que visita un numero a una expressio d'un camp calculat.
    def visitNumeroCamp(self, ctx):
        # Llegim el numero i retornem el seu int.
        [numero] = list(ctx.getChildren())
        return int(numero.getText())

    # Funcio que visita l'Id d'un camp a una expressio d'un camp calculat.
    def visitIdCamp(self, ctx):
        # Llegim el numero i retornem el seu camp a la taula self.df.
        [idCamp] = list(ctx.getChildren())
        return self.df[idCamp.getText()]

    # Funcio que visita parentesis a una expressio d'una condicio
    def visitParentesisCondicio(self, ctx):
        # Llegim la condicio.
        [_, condicio, _] = list(ctx.getChildren())
        # Retornem la condicio.
        return (self.visit(condicio))

    # Funcio auxiliar que retorna l'expressio corresponent.
    def opCondicio(self, expr1, expr2, operador):
        if (operador.getText() == '<'):
            return (expr1 < expr2)
        else:
            return (expr1 == expr2)

    # Funcio que visita la operacio en una condicio entre l'id d'un Camp i un
    # numero.
    def visitOpCondicioID1(self, ctx):
        [idCamp, operador, numero] = list(ctx.getChildren())
        return self.opCondicio(
            self.df[idCamp.getText()], int(numero.getText()), operador)

    # Funcio que visita la operacio en una condicio entre un numero i l'id
    # d'un Camp.
    def visitOpCondicioID2(self, ctx):
        [numero, operador, idCamp] = list(ctx.getChildren())
        return self.opCondicio(int(numero.getText()),
                               self.df[idCamp.getText()], operador)

    # Funcio que visita la operacio en una condicio entre dos ids d'un Camp.
    def visitOpCondicioID3(self, ctx):
        [idCamp1, operador, idCamp2] = list(ctx.getChildren())
        return self.opCondicio(
            self.df[idCamp1.getText()], self.df[idCamp2.getText()], operador)

    # Funcio que visita and o or a una condicio.
    def visitAndorCondicio(self, ctx):
        # Llegim la condicio1 i condicio2.
        [condicio1, op, condicio2] = list(ctx.getChildren())
        # Apliquem and o or en funcio del que hi hagi a op.
        if (op.getText() == 'and'):
            return (self.visit(condicio1) & self.visit(condicio2))
        else:
            return (self.visit(condicio1) | self.visit(condicio2))

    # Funcio que visita un not a una condicio.
    def visitNotCondicio(self, ctx):
        # Llegim la condicio.
        [_, condicio] = list(ctx.getChildren())
        # Retornem la condicio negada.
        return (~ self.visit(condicio))

    # Funcio que visita una Subquery.
    def visitSubquery(self, ctx):
        [idcamp1, _, _, selectStatement, _] = list(ctx.getChildren())
        # Desem l'actual self.df a df.
        df = self.df
        # Visitem la nova taula, que acabara a self.df.
        self.visit(selectStatement)
        # Desem a df2 la nova taula i tornem a posar df a self.df.
        df2 = self.df
        self.df = df
        # Ens quedem nomes amb les files de self.df que siguin a df2.
        return (self.df[idcamp1.getText()].isin(df2.iloc[:, 0]))


# Main del programa.
if __name__ == "__main__":
    # Creem un area de text amb una key aleatoria.
    text = st.text_area("Query:", key='hola')

    # Creacio d'un boto Submit
    if st.button("Submit"):
        input_stream = InputStream(text)
        lexer = pandaQLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = pandaQParser(token_stream)
        tree = parser.root()

        if parser.getNumberOfSyntaxErrors() == 0:
            visitor = pandaQ()
            visitor.visit(tree)
        else:
            print(parser.getNumberOfSyntaxErrors(), 'errors de sintaxi.')
            print(tree.toStringTree(recog=parser))
