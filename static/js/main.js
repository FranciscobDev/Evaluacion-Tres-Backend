/**
 * CheckDent - Script Principal de Comportamiento e Interfaz
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Desvanecer alertas informativas automáticamente tras 6 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // 2. Formateador dinámico de RUT chileno en inputs
    const rutInputs = document.querySelectorAll('input#id_rut');
    rutInputs.forEach(function (input) {
        input.addEventListener('input', function (e) {
            let valor = e.target.value.replace(/[^0-9kK]/g, '').toUpperCase();
            if (valor.length > 1) {
                const cuerpo = valor.slice(0, -1);
                const dv = valor.slice(-1);
                const cuerpoFormateado = cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
                e.target.value = `${cuerpoFormateado}-${dv}`;
            } else {
                e.target.value = valor;
            }
        });
    });
});

