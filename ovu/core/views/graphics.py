import io
from random import sample

from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
# from pandas import np
import numpy as np
import matplotlib.pyplot as plt

from ovu.core.utils import MyBar


def plot(request):
    # https://www.hektorprofe.net/tutorial/graficos-matplotlib-django

    # Creamos los datos para representar en el gráfico
    x = range(1, 11)
    y = sample(range(20), len(x))
    datos: dict = request.session.get('datos')
    headers: list = request.session.get('headers')

    del request.session['datos']
    del request.session['headers']

    print('----------')
    print(headers)
    del headers[0]
    print(headers)
    print(datos)
    print('----------')
    p = MyBar(labels=headers, values=datos)

    print('Graphics')
    print(list(dict.fromkeys(headers)))
    print(datos)
    print('Graphics')

    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(p.to_draw())
    canvas.print_png(buf)

    # Creamos la respuesta enviando los bytes en tipo imagen png
    response = HttpResponse(buf.getvalue(), content_type='image/png')

    # Limpiamos la figura para liberar memoria
    p.to_clear()

    # Añadimos la cabecera de longitud de fichero para más estabilidad
    response['Content-Length'] = str(len(response.content))

    # Devolvemos la response
    return response


def dashboard_plot(request):
    # Creamos los datos para representar en el gráfico
    x = [1, 2, 3]

    y = [4, 5, 6]

    x1 = np.linspace(0, 10, 1000)

    p, axes = plt.subplots(nrows=2, ncols=2)

    axes[0, 0].plot(x, y)

    axes[0, 1].plot(x1, np.sin(x1))

    axes[1, 0].plot(x1, np.cos(x1))

    axes[1, 1].plot(range(10))

    p.tight_layout()

    # Como enviaremos la imagen en bytes la guardaremos en un buffer
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(p)
    canvas.print_png(buf)

    # Creamos la respuesta enviando los bytes en tipo imagen png
    response = HttpResponse(buf.getvalue(), content_type='image/png')

    # Limpiamos la figura para liberar memoria
    # p.to_clear()

    # Añadimos la cabecera de longitud de fichero para más estabilidad
    response['Content-Length'] = str(len(response.content))

    # Devolvemos la response
    return response
