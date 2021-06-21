from proyecto import app
from flask import jsonify,render_template, request, redirect, url_for
from proyecto.forms import PurchaseForm
import datetime
import sqlite3
import json
import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

BBDD = './data/movimientos.db'
API_KEY=app.config['API_KEY']

cryptos = ("BTC","ETH", "LTC", "BNB", "EOS", "XLM", "TRX",  "XRP", "BCH", "USDT", "BSV", "ADA")

def api(cryptoFrom, cryptoTo):

    url= "https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount=1&symbol={}&convert={}&CMC_PRO_API_KEY=<1ce220db-5044-462d-9bdb-f46d27d98f63>".format(cryptoTo, cryptoFrom)

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }

    session = Session()
    session.headers.update(headers)

    respuesta = session.get(url)
    data = json.loads(respuesta.text)
    try:
        return ('', data['data']['quote'][cryptoFrom]['price'])
    except:
        errorCodeAPI = data['status']['error_code']
        return ('error', errorCodeAPI)

def ApiError(codigo):
    if codigo == 1001:
        msg = "1001 [API_KEY_INVALID] Esta clave de API no es válida."
    elif codigo == 1002:
        msg= "1002 [API_KEY_MISSING] Falta la clave de API."
    elif codigo == 1003:
        msg= "1003 [API_KEY_PLAN_REQUIRES_PAYEMENT] Su clave API debe estar activada. Vaya a pro.coinmarketcap.com/account/plan."
    elif codigo == 1004:
        msg= "1004 [API_KEY_PLAN_PAYMENT_EXPIRED] El plan de suscripción de su clave API ha vencido."
    elif codigo == 1005:
        msg= "1005 [API_KEY_REQUIRED] Se requiere una clave API para esta llamada."
    elif codigo == 1006:
        msg= "1006 [API_KEY_PLAN_NOT_AUTHORIZED] Su plan de suscripción de clave API no es compatible con este punto final."
    elif codigo == 1007:
        msg= "1007 [API_KEY_DISABLED] Esta clave de API ha sido inhabilitada. Comuníquese con el soporte."
    elif codigo == 1008:
        msg= "1008 [API_KEY_PLAN_MINUTE_RATE_LIMIT_REACHED] Has superado el límite de frecuencia de solicitudes HTTP de tu clave API. Los límites de frecuencia se restablecen cada minuto."
    elif codigo == 1009:
        msg= "1009 [API_KEY_PLAN_DAILY_RATE_LIMIT_REACHED] Has superado el límite de frecuencia diario de tu clave API."
    elif codigo == 1010:
        msg= "1010 [API_KEY_PLAN_MONTHLY_RATE_LIMIT_REACHED] Has superado el límite de frecuencia mensual de tu clave API"
    elif codigo == 1011:
        msg= "1011 [IP_RATE_LIMIT_REACHED] Alcanzado límite de velocidad de la IP"

    return msg

def dataQuery(consulta):

    conex = sqlite3.connect(BBDD)
    cursor = conex.cursor()

    movs = cursor.execute(consulta).fetchall()

    if len(movs) == 0:
        movs = None

    conex.commit()
    conex.close()

    return movs

def Saldo():
    Balance = []
    for moneda in cryptos:
        cryptoBalanceCoin = dataQuery(format(moneda, moneda))
        if cryptoBalanceCoin[0] == (None,):
            cryptoBalanceCoin=0
            Balance.append(cryptoBalanceCoin)
        else:
            Balance.append(cryptoBalanceCoin[0][0])
    return Balance

@app.route("/")
def index():
        try:
            registros = dataQuery("SELECT date, time, moneda_from, cantidad_from, moneda_to, cantidad_to FROM MOVIMIENTOS;")
            return render_template("index.html", menu='index', registros = registros)

        except sqlite3.Error:
            registros = None
            errorDB = "Error en la base de datos, intentelo un poco más tarde"
            return render_template("index.html", menu='index', errorDB=errorDB, registros=registros)

@app.route("/purchase", methods=['GET', 'POST'])
def purchase():

    form = PurchaseForm(request.form)
    selecFrom=request.values.get("slct_from")
    selecTo=request.values.get("slct_to")
    units=request.values.get("inputCantidad")
    quant = 0
    pu = 0

    if request.method == 'GET':

        return render_template("purchase.html", menu='purchase', form=form, data=[quant,pu])

    if request.values.get("submitCalcular"):
        if not form.validate():
            quant = 0
            pu = 0
            validError = "Operación no realizada, la Cantidad tiene que ser un valor numérico y mayor a 0"
            return render_template("purchase.html", menu='purchase',form=form , validError=validError, data=[quant,pu])

        # confirmación moneda distinta

        if selecFrom == selecTo:
            quant = 0
            pu = 0
            cryptoError = "Operación incorrecta, debe elegir dos monedas distintas"
            return render_template("purchase.html", menu='purchase',form=form , cryptoError=cryptoError, data=[quant,pu])

        # confirmación  de calculo entre criptomendas

        if selecFrom == 'EUR' and selecTo != 'BTC':
            quant = 0
            pu = 0
            cryptoIncompatible = "Operación no realizada, no se puede comprar {} con euros".format(selecTo)
            return render_template("purchase.html", menu='purchase',form=form , cryptoIncompatible=cryptoIncompatible, data=[quant,pu])

        if selecTo == 'EUR'and selecFrom != "BTC":
            quant = 0
            pu = 0
            cryptoIncompatible = "Operación no realizada, no se puede Comprar  euros con {}".format(selecFrom)
            return render_template("purchase.html", menu='purchase', form=form , cryptoIncompatible=cryptoIncompatible, data=[quant,pu])

        apiConsult = api(selecFrom, selecTo)
        if apiConsult[0] =='error':
            quant = 0
            pu = 0
            messageError = ApiError(apiConsult[1])
            errorAPI = "Error API".format(messageError)
            return render_template("purchase.html", menu='purchase', form=form , errorAPI=errorAPI, data=[quant,pu])
        else:
            dataQuant = apiConsult[1]

        quant = float(dataQuant)*float(units)
        pu = dataQuant

        return render_template("purchase.html", menu='purchase', form=form, data=[quant, pu, selecFrom])

    if request.values.get("submitCompra"):

        if not form.validate():
            quant = 0
            pu = 0
            validError = "Operación no realizada, la Cantidad tiene que ser un valor numérico y mayor a 0"
            return render_template("purchase.html", menu='purchase', form=form , validError=validError, data=[quant,pu])

        # confirmación de monedas diferentes

        if selecFrom == selecTo:
            quant = 0
            pu = 0
            cryptoError = "Operación incorrecta, debe elegir dos monedas distintas"
            return render_template("purchase.html", menu='purchase', form=form , cryptoError=cryptoError, data=[quant,pu])

        # confirmacion de compatibilidad de compra entre monedas

        if selecFrom == 'EUR' and selecTo != 'BTC':
            quant = 0
            pu = 0
            cryptoIncompatible = "Operacion incorrecta, no se puede comprar {} con Euros".format(selecTo)
            return render_template("purchase.html", menu='purchase', form=form , cryptoIncompatible=cryptoIncompatible, data=[quant,pu])

        if selecTo == 'EUR'and selecFrom != "BTC":
            quant = 0
            pu = 0
            cryptoIncompatible = "Operación incorrecta, no se puede comprar euros con {}".format(selecFrom)
            return render_template("purchase.html", menu='purchase', form=form , cryptoIncompatible=cryptoIncompatible, data=[quant,pu])

        #Calculo de saldo de la moneda con la que se quiere comprar
        if selecFrom == 'EUR':
            saldo = 9999999999
        else:
            try:
                saldoStr = dataQuery(format(selecFrom, selecFrom))
            except sqlite3.Error:
                quant = 0
                pu = 0
                errorDB = "Error en la base de datos, intentelo en unos minutos"
                return render_template("purchase.html", menu='purchase', form=form , errorDB=errorDB, data=[quant,pu])

            if saldoStr[0] == (None,):
                saldo = 0
            else:
                saldo = saldoStr[0][0]

        if selecFrom == 'EUR' or saldo != 0:

            dt = datetime.datetime.now()
            fecha=dt.strftime("%d/%m/%Y")
            hora=dt.strftime("%H:%M:%S")
            apiConsult = api(selecFrom, selecTo)
            if apiConsult[0] =='error':
                quant = 0
                pu = 0
                messageError = ApiError(apiConsult[1])
                errorAPI = "Error en la API".format(messageError)
                return render_template("purchase.html", menu='purchase', form=form , errorAPI=errorAPI, data=[quant,pu])
            else:
                dataQuant = apiConsult[1]
                quant = float(dataQuant)*float(units)

            # Comprobación de saldo suficiente con la moneda que se compra

            if saldo >= quant or selecFrom == 'EUR':

                conex = sqlite3.connect(BBDD)
                cursor = conex.cursor()
                mov = "INSERT INTO MOVIMIENTOS(date, time, moneda_from, cantidad_from, moneda_to, cantidad_to  ) VALUES(?, ?, ?, ?, ?, ?);"

                try:
                    cursor.execute(mov, (fecha, hora, selecFrom, float(quant), selecTo, float(units)))
                except sqlite3.Error:
                    quant = 0
                    pu = 0
                    errorDB = "Error en la base de datos, intentelo en unos minutos"
                    return render_template("purchase.html", menu='purchase', form=form , errorDB=errorDB, data=[quant,pu])

                conex.commit()
                try:
                    registros = dataQuery("SELECT date, time, moneda_from, cantidad_from, moneda_to, cantidad_to FROM MOVIMIENTOS;")
                    conex.close()
                    return render_template("index.html", menu='index', form=form, registros=registros)
                except sqlite3.Error:
                    quant = 0
                    pu = 0
                    errorDB = "Error en la base de datos, intentelo en unos minutos"
                    return render_template("purchase.html", menu='purchase', form=form , errorDB=errorDB, data=[quant,pu])
            else:
                pu = dataQuant
                sinSaldo = "No dispone de saldo Sufiente en {} para realizar esta operación".format(selecFrom)
                return render_template("purchase.html", menu='purchase', form=form , sinSaldo=sinSaldo, data=[quant,pu])
        else:
            quant = 0
            pu = 0
            alert = "No exite saldo de compra en la moneda {}".format(selecFrom)
            return render_template("purchase.html", menu='purchase', form=form, data=[quant, pu, selecFrom], alert=alert)

@app.route("/status")
def inverter():

    # Calcular Inversion
    try:
        movOrNot = dataQuery("SELECT date, time, moneda_from, cantidad_from, moneda_to, cantidad_to, FROM MOVIMIENTOS;")
    except sqlite3.Error:
        totalInver = 0
        valorAct = 0
        dif = 0
        errorDB = "Error en la base de datos, intentelo en unos minutos"
        return render_template("status.html", menu='status', errorDB=errorDB, movOrNot=True)

    if movOrNot == None:
        return render_template("status.html", menu='status', movOrNot=True)

    try:
        InverFrom= dataQuery('SELECT SUM(cantidad_from) FROM MOVIMIENTOS WHERE moneda_from LIKE "%EUR%";')
        InverTo= dataQuery('SELECT SUM(cantidad_from) FROM MOVIMIENTOS WHERE moneda_to LIKE "%EUR%";')
    except sqlite3.Error:
        totalInver = 0
        valorAct = 0
        dif = 0
        errorDB = "Error en la base de datos, inténtelo unos minutos"
        return render_template("status.html", menu='status', errorDB=errorDB, movOrNot=True)

    totalInverFrom = 0
    totalInverTo = 0
    for i in range(len(InverFrom)):
        if InverFrom[i] == (None,):
            totalInverFrom += 0
        else:
            InverFromInt = InverFrom[i][0]
            totalInverFrom += InverFromInt

    for i in range(len(InverTo)):
        if InverTo[i] == (None,):
            totalInverTo += 0
        else:
            InverToInt = InverTo[i][0]
            totalInverTo += InverToInt

    totalInver = totalInverFrom + totalInverTo

    # Calcular saldo de monedas
    try:
        Saldo()
    except sqlite3.Error:
        totalInver = 0
        valorAct = 0
        dif = 0
        errorDB = "Error en la base de datos, inténtelo mas tarde"
        return render_template("status.html", menu='status', errorDB=errorDB, movOrNot=True)

    # Calculo Valor Actual de todas las monedas en € y totalizarlas en Status
    i = 0
    monedaValorActual = {}
    valorAct = 0
    for moneda in cryptos:
        apiConsult = api('EUR',moneda)
        if apiConsult[0] =='error':
            totalInver = 0
            valorAct = 0
            dif = 0
            messageError = ApiError(apiConsult[1])
            errorAPI = "ERROR EN API - {}".format(messageError)
            return render_template("status.html", menu='status', errorAPI=errorAPI, totalInver=totalInver, cryptoBalance=Saldo(), valorAct=valorAct, dif=dif)
        else:
            cotizacion = apiConsult[1]
            saldocript = Saldo()[i]
            monedaValorActual[moneda] = cotizacion * saldocript
            valorAct += monedaValorActual[moneda]
            i += 1

    # Calculo Beneficio/Perdida
    dif = valorAct - totalInver

    return render_template("status.html", menu='status', totalInver=totalInver, cryptoBalance=Saldo(), valorAct=valorAct, dif=dif)

      