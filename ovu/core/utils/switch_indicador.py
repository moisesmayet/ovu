def indicador_switcher(case):
    indicador_switcher = {
        'CES.01': 'Categorias',
        'CES.02': 'Región/Provincia',
        'CES.03': 'Nivel/Año',
        'CES.04': 'Desagregaciones',
        'CES.05': 'Desagregaciones',
        'CES.06': 'Desagregaciones',
        'CES.07': 'Desagregaciones',
        'OA.01': 'Oferta académica',
        'OA.02': 'Escuela',
        'OA.03': 'No hay datos',
        'OA.04': 'Programa de grado',
        'DU.01': 'Programas',
        'DU.02': 'Programas',
        'DU.03': 'Programas',
        'DU.04': 'Programas',
        'DU.05': 'Programas',
        'DU.06': 'No hay datos',
        'DU.07': 'Posición de instituciones',
        'PA.01': 'Programas',
        'PA.02': 'Programas',
        'PA.03': 'Programas',
        'PA.04': 'Programas',
        'PA.05': 'No hay datos',
        'PA.06': 'Programas',
    }
    return indicador_switcher.get(case, 'Categorias')