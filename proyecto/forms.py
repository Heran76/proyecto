from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, Label, FloatField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length
from wtforms.widgets import Select

class PurchaseForm(FlaskForm):
    slct_from = SelectField('From', choices=[('EUR', 'EUR - EURO'), ('BTC', 'BTC - Bitcoin'), ('ETH', 'ETH - Ether'), ('XRP', 'XRP - Ripple'), ('LTC', 'LTC - Litecoin'), ('BCH', 'BCH - Bitcoin Cash'), ('BNB', 'BNB - Binance Coin'), ('USDT', 'USDT - Tether'), ('EOS', 'EOS - EOS'), ('BSV', 'BSV - Bitcoin SV'), ('XLM', 'XLM - Stellar'), ('ADA', 'ADA - Cardano'), ('TRX', 'TRX - TRON')])
    slct_to = SelectField('To', choices=[('EUR', 'EUR - EURO'), ('BTC', 'BTC - Bitcoin'), ('ETH', 'ETH - Ether'), ('XRP', 'XRP - Ripple'), ('LTC', 'LTC - Litecoin'), ('BCH', 'BCH - Bitcoin Cash'), ('BNB', 'BNB - Binance Coin'), ('USDT', 'USDT - Tether'), ('EOS', 'EOS - EOS'), ('BSV', 'BSV - Bitcoin SV'), ('XLM', 'XLM - Stellar'), ('ADA', 'ADA - Cardano'), ('TRX', 'TRX - TRON')])
    inputCantidad = FloatField('Cantidad', validators=[InputRequired(), NumberRange(min=0.00001, max=99999999)])

    submitCalcular = SubmitField('Calcular')
    submitCompra = SubmitField('Aceptar')