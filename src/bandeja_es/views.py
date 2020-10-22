from django.shortcuts import render

# Create your views here.

    # OPCION 2 (MAS FACTIBLE)
    # select Documento.num_docuemto, Documento.nombre, Documento.owner, Revision.estado_contratista, Historial.fecha
    # from Docuemto, Revision, Historial
    # join revision on Documento.pk = revision.Documento
    # when (documento.pk == Historial.documento)
