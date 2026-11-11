def presupuesto_dental(req):
    """
    Context Processor personalizado (Módulo 4 - Criterio 2.1.4):
    Inyecta globalmente en el Navbar la cantidad total de sesiones/prestaciones
    y el monto acumulado en la sesión transitoria 'presupuesto_dental'.
    """
    presup = req.session.get('presupuesto_dental', {})
    tot_items = sum(int(itm.get('sesiones', 0)) for itm in presup.values())
    subtot_acum = sum(
        int(itm.get('arancel', 0)) * int(itm.get('sesiones', 0))
        for itm in presup.values()
    )
    return {
        'presupuesto_total_items': tot_items,
        'presupuesto_subtotal_global': subtot_acum,
    }

