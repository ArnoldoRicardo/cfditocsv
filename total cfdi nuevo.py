#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import glob
import xml.dom.minidom
# import ipdb

# from datetime import datetime


def datos(file):
    xmldoc = xml.dom.minidom.parse(file)
    print(file)

    comprobante = xmldoc.getElementsByTagName("cfdi:Comprobante")
    try:
        version = comprobante[0].attributes.get("version").value
    except Exception, e:
        version = comprobante[0].attributes.get("Version").value

    # ipdb.set_trace()
    # print version

    if float(version) <= 3.2:
        claves = {
            "rfc": "rfc",
            "subtotal": "subTotal",
            "total": "total",
            "metododepago": "metodoPago",
            "fecha": "fecha",
            "cantidad": "cantidad",
            "descripcion": "descripcion",
        }
    else:
        claves = {
            "rfc": "Rfc",
            "subtotal": "SubTotal",
            "total": "Total",
            "metododepago": "MetodoPago",
            "fecha": "Fecha",
            "cantidad": "Cantidad",
            "descripcion": "Descripcion",
        }

    # rfc
    emisor = xmldoc.getElementsByTagName("cfdi:Emisor")
    rfcEmisor = emisor[0].attributes.get(claves["rfc"]).value

    receptor = xmldoc.getElementsByTagName("cfdi:Receptor")
    rfcReceptor = receptor[0].attributes.get(claves["rfc"]).value

    # totales
    subTotal = comprobante[0].attributes.get(claves["subtotal"]).value
    total = comprobante[0].attributes.get(claves["total"]).value
    try:
        metodo = comprobante[0].attributes.get(claves["metododepago"]).value
    except Exception, e:
        metodo = "NA"

    # lugar
    emisorDomicilio = xmldoc.getElementsByTagName("cfdi:DomicilioFiscal")
    try:
        lugar = comprobante[0].attributes.get(
            "LugarExpedicion").value + " " + emisorDomicilio[0].attributes.get("municipio").value
    except Exception, e:
        try:
            lugar = emisorDomicilio[0].attributes.get("municipio").value
        except Exception, e:
            lugar = "NA"

    # fecha
    strTime = comprobante[0].attributes.get(claves["fecha"]).value
    # time = datetime.strptime(strTime, "%Y-%m-%dT%H:%M:%S")
    # fecha = time.date()

    # cfdi:Impuestos
    ivat = 0
    isrt = 0
    ivar = 0
    isrr = 0
    try:
        impuesto = xmldoc.getElementsByTagName("cfdi:Impuestos")[0]
        if impuesto.getElementsByTagName("cfdi:Traslados"):
            trasladado = impuesto.getElementsByTagName("cfdi:Traslados")[0]
            traslados = trasladado.getElementsByTagName("cfdi:Traslado")
            for traslado in traslados:
                # ipdb.set_trace()
                if traslado.attributes.get("Impuesto").value == "002":
                    ivat += float(traslado.attributes.get("Importe").value)
                if traslado.attributes.get("Impuesto").value == "001":
                    isrt += float(traslado.attributes.get("Importe").value)
        if impuesto.getElementsByTagName("cfdi:Retenciones"):
            retenidos = impuesto.getElementsByTagName("cfdi:Retenciones")[0]
            retenciones = retenidos.getElementsByTagName("cfdi:Retencion")
            for retencion in retenciones:
                if retencion.attributes.get("Impuesto").value == "002":
                    ivar += float(retencion.attributes.get("Importe").value)
                if retencion.attributes.get("Impuesto").value == "001":
                    isrr += float(retencion.attributes.get("Importe").value)
    except Exception, e:
        impuesto = "0"

    # conceptos
    concep = ""
    conceptos = xmldoc.getElementsByTagName("cfdi:Concepto")
    for concepto in conceptos:
        concep += concepto.attributes.get(claves["cantidad"]).value + \
            " " + concepto.attributes.get(claves["descripcion"]).value + ", "

    # ipdb.set_trace()

    return {
        'total': float(total),
        'subTotal': float(subTotal),
        'rfcEmisor': rfcEmisor,
        'rfcReceptor': rfcReceptor,
        'fecha': strTime,
        'ivat': ivat,
        'isrt': isrt,
        'ivar': ivar,
        'isrr': isrr,
        'metodo': metodo.encode('utf-8'),
        'conceptos': concep.encode('utf-8'),
        'lugar': lugar.encode('utf-8')
    }


catedraticos = (
    '',
)


def main(args):
    suma = 0
    titulos = ['archivo',
               'Total',
               "metodo",
               'subtotoal',
               'tipo',
               'conceptos',
               'rfc emisor',
               'rfc receptor',
               'fecha',
               'ivaTrasladado',
               'isrTrasladado',
               'ivaRetenido',
               'isrRetenido'
               ]
    import csv
    out = csv.writer(open("concetrado.csv", "w"), delimiter=';',
                     quoting=csv.QUOTE_ALL, lineterminator='\r')
    out.writerow(titulos)
    for argument in args:
        t = datos(argument)
        row = []
        if not t["rfcEmisor"] in catedraticos:
            suma += t["total"]
            row.append(argument)
            row.append(t['total'])
            row.append(t['metodo'])
            row.append(t['subTotal'])
            row.append('')
            row.append(t['conceptos'])
            row.append(t['rfcEmisor'])
            row.append(t['rfcReceptor'])
            row.append(t['fecha'])
            row.append(t['ivat'])
            row.append(t['isrt'])
            row.append(t['ivar'])
            row.append(t['isrr'])
            print(argument)
            print(row)
            out.writerow(row)


if __name__ == '__main__':
    if len(sys.argv[1:]) > 0:
        main(sys.argv[1:])
    else:
        files = glob.glob("*.xml")
        if files:
            main(files)
        else:
            raw_input("no hay archivos xml")
