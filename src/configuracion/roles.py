ROLES = (
    ('','-----'),
    (1, 'Administrador'), #Acceso total

    #Sin panel de configuracion
    (2, 'Revisor'), #Tiene acceso al panel de carga y Baes pero con aprobacion de su jefe o administrador
    (3, 'Vizualizador'), #Tiene acceso a solo Analitica buscador y status
    (4, 'Administrador (invitado)') #No puede configurar la plataforma
)