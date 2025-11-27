from django.db import models
from django.utils import timezone # Importado para referencia, aunque no se usa en los campos de abajo

# 1. Modelos de Base (Dependencias)
# ----------------------------------------------------------------------

class Rol_Produccion(models.Model):
    """Define los roles disponibles en una producción (Ej: Director, DP, Gaffer)."""
    # id_rol (PK) - models.AutoField implícito
    nombre_rol = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Rol")
    descripcion_rol = models.TextField(blank=True, null=True, verbose_name="Descripción del Rol")
    departamento = models.CharField(max_length=50, verbose_name="Departamento")
    salario_promedio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Salario Promedio")
    habilidades_requeridas = models.TextField(blank=True, null=True, verbose_name="Habilidades Requeridas")

    class Meta:
        verbose_name = "Rol de Producción"
        verbose_name_plural = "Roles de Producción"

    def __str__(self):
        return self.nombre_rol

# ----------------------------------------------------------------------

class Miembro_Equipo(models.Model):
    """Representa a una persona que forma parte del equipo de producción."""
    # id_miembro (PK) - models.AutoField implícito
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
    # RELACIÓN: Muchos Miembros a un Rol (Aunque el esquema sugiere una relación por el nombre, 
    # la buena práctica es enlazar con FK al modelo completo).
    # He renombrado 'rol' a 'rol_produccion' para evitar conflicto con el objeto del modelo.
    rol_produccion = models.ForeignKey(
        Rol_Produccion, 
        on_delete=models.SET_NULL, # Si se borra el Rol, se deja en NULL
        null=True, 
        blank=True, 
        verbose_name="Rol en Producción"
    )
    
    email = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_contratacion = models.DateField(verbose_name="Fecha de Contratación")
    salario_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario Base")
    especialidad_tecnica = models.CharField(max_length=100, blank=True, null=True, verbose_name="Especialidad Técnica")
    disponibilidad = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Miembro del Equipo"
        verbose_name_plural = "Miembros del Equipo"

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol_produccion or 'Sin Rol'})"

# ----------------------------------------------------------------------

class Proyecto_Audiovisual(models.Model):
    """Modelo principal que representa un proyecto audiovisual (película, serie, corto, etc.)."""
    # id_proyecto (PK) - models.AutoField implícito
    titulo = models.CharField(max_length=255, unique=True)
    tipo_produccion = models.CharField(max_length=50, verbose_name="Tipo de Producción")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin_estimada = models.DateField(blank=True, null=True, verbose_name="Fecha Fin Estimada")
    presupuesto = models.DecimalField(max_digits=15, decimal_places=2)
    estado_proyecto = models.CharField(max_length=50, verbose_name="Estado del Proyecto")
    
    # RELACIÓN: id_director -> Miembro_Equipo (Muchos Proyectos a un Director)
    director = models.ForeignKey(
        Miembro_Equipo, 
        on_delete=models.SET_NULL, # Si se borra el Miembro, se deja en NULL
        null=True, 
        blank=True, 
        related_name='proyectos_dirigidos', # Para acceder desde el director: director.proyectos_dirigidos.all()
        verbose_name="Director"
    )
    
    descripcion = models.TextField(blank=True, null=True)
    distribucion_prevista = models.CharField(max_length=100, blank=True, null=True, verbose_name="Distribución Prevista")

    class Meta:
        verbose_name = "Proyecto Audiovisual"
        verbose_name_plural = "Proyectos Audiovisuales"

    def __str__(self):
        return f"{self.titulo} ({self.estado_proyecto})"

# ----------------------------------------------------------------------

# 2. Modelos de Detalle y Gestión
# ----------------------------------------------------------------------

class Escena(models.Model):
    """Detalle de una escena dentro de un proyecto."""
    # id_escena (PK) - models.AutoField implícito
    
    # RELACIÓN: id_proyecto -> Proyecto_Audiovisual
    proyecto = models.ForeignKey(
        Proyecto_Audiovisual, 
        on_delete=models.CASCADE, # Si se borra el Proyecto, se borran sus Escenas
        related_name='escenas', 
        verbose_name="Proyecto"
    )
    
    numero_escena = models.IntegerField(verbose_name="Número de Escena")
    descripcion_escena = models.TextField(verbose_name="Descripción de la Escena")
    localizacion = models.CharField(max_length=255, verbose_name="Localización")
    fecha_grabacion_estimada = models.DateField(blank=True, null=True, verbose_name="Fecha Grabación Estimada")
    hora_grabacion = models.TimeField(blank=True, null=True, verbose_name="Hora de Grabación")
    actores_involucrados = models.TextField(blank=True, null=True, verbose_name="Actores Involucrados") # Nota: Mejor sería M2M
    equipos_especiales = models.TextField(blank=True, null=True, verbose_name="Equipos Especiales")

    class Meta:
        verbose_name = "Escena"
        verbose_name_plural = "Escenas"
        unique_together = ('proyecto', 'numero_escena') # Una escena debe ser única dentro de un proyecto.

    def __str__(self):
        return f"{self.proyecto.titulo} - Escena {self.numero_escena}"

# ----------------------------------------------------------------------

class Material_Grabado(models.Model):
    """Representa los archivos de material grabado asociados a una escena."""
    # id_material (PK) - models.AutoField implícito
    
    # RELACIÓN: id_escena -> Escena
    escena = models.ForeignKey(
        Escena, 
        on_delete=models.CASCADE, # Si se borra la Escena, se borra el Material Grabado
        related_name='materiales_grabados', 
        verbose_name="Escena"
    )
    
    tipo_material = models.CharField(max_length=50, verbose_name="Tipo de Material")
    duracion_segundos = models.IntegerField(verbose_name="Duración (segundos)")
    formato_archivo = models.CharField(max_length=20, verbose_name="Formato de Archivo")
    fecha_grabacion_real = models.DateTimeField(verbose_name="Fecha y Hora Real de Grabación")
    ruta_almacenamiento = models.CharField(max_length=255, unique=True, verbose_name="Ruta de Almacenamiento")
    notas_tecnicas = models.TextField(blank=True, null=True, verbose_name="Notas Técnicas")
    version = models.CharField(max_length=10, default='V1')

    class Meta:
        verbose_name = "Material Grabado"
        verbose_name_plural = "Material Grabado"

    def __str__(self):
        return f"Material {self.id} de Escena {self.escena.numero_escena} ({self.formato_archivo})"

# ----------------------------------------------------------------------

class Presupuesto_Detalle(models.Model):
    """Desglose de los gastos estimados y reales de un proyecto."""
    # id_item_presupuesto (PK) - models.AutoField implícito
    
    # RELACIÓN: id_proyecto -> Proyecto_Audiovisual
    proyecto = models.ForeignKey(
        Proyecto_Audiovisual, 
        on_delete=models.CASCADE, # Si se borra el Proyecto, se borran sus Detalles de Presupuesto
        related_name='detalles_presupuesto',
        verbose_name="Proyecto"
    )
    
    categoria_gasto = models.CharField(max_length=100, verbose_name="Categoría de Gasto")
    descripcion_gasto = models.TextField(verbose_name="Descripción del Gasto")
    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Estimado")
    monto_real = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Monto Real")
    fecha_gasto = models.DateField(blank=True, null=True, verbose_name="Fecha del Gasto")
    aprobado_por = models.CharField(max_length=100, blank=True, null=True, verbose_name="Aprobado Por")
    tipo_moneda = models.CharField(max_length=10, default='USD', verbose_name="Tipo de Moneda")

    class Meta:
        verbose_name = "Detalle de Presupuesto"
        verbose_name_plural = "Detalles de Presupuesto"

    def __str__(self):
        return f"{self.proyecto.titulo} - {self.categoria_gasto}"

# ----------------------------------------------------------------------

class Contrato_Talento(models.Model):
    """Contratos individuales firmados para un proyecto."""
    # id_contrato (PK) - models.AutoField implícito
    
    # RELACIÓN 1: id_proyecto -> Proyecto_Audiovisual
    proyecto = models.ForeignKey(
        Proyecto_Audiovisual, 
        on_delete=models.CASCADE, # Si se borra el Proyecto, se borran los Contratos
        related_name='contratos',
        verbose_name="Proyecto"
    )
    
    # RELACIÓN 2: id_miembro -> Miembro_Equipo
    miembro = models.ForeignKey(
        Miembro_Equipo, 
        on_delete=models.CASCADE, # Si se borra el Miembro, se borran los Contratos asociados
        related_name='contratos_firmados',
        verbose_name="Miembro del Equipo"
    )
    
    fecha_firma = models.DateField(verbose_name="Fecha de Firma")
    salario_acordado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salario Acordado")
    clausulas_especiales = models.TextField(blank=True, null=True, verbose_name="Cláusulas Especiales")
    duracion_contrato = models.CharField(max_length=50, verbose_name="Duración del Contrato")
    rol_especifico = models.CharField(max_length=100, verbose_name="Rol Específico en Contrato")

    class Meta:
        verbose_name = "Contrato de Talento"
        verbose_name_plural = "Contratos de Talento"
        # Un miembro solo debería tener un contrato activo por proyecto
        unique_together = ('proyecto', 'miembro') 

    def __str__(self):
        return f"Contrato de {self.miembro.nombre} para {self.proyecto.titulo}"
