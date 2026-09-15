import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import modelo as m

billetera1 = m.Billetera(disponible=1000000)
print("Disponible:", billetera1.consultar_disponible())
print("Numero de cuenta:", billetera1.numeroCuenta)

billetera1.retirar_dinero(monto=50000)
print("Disponible tras retiro:", billetera1.consultar_disponible())