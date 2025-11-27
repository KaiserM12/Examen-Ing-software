from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Mesa(models.Model):
    ESTADOS = [('LIBRE', 'Libre'), ('OCUPADA', 'Ocupada')]
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=4)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='LIBRE')

    def __str__(self):
        return f"Mesa {self.numero} ({self.estado})"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    categoria = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    ingredientes = models.TextField(blank=True, null=True)
    disponible = models.BooleanField(default=True) 
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADOS_PEDIDO = [
        ('CREANDO', 'Creando'),
        ('EN_COCINA', 'En Cocina'),
        ('LISTO', 'Listo para Servir'),
        ('PAGADO', 'Pagado')
    ]

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='CREANDO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        return sum(item.total_linea for item in self.detalles.all())
    
    @property
    def total_items(self):
        return sum(item.cantidad for item in self.detalles.all())

    def __str__(self):
        return f"Pedido #{self.id} - Mesa {self.mesa.numero if self.mesa else '?'}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)

    @property
    def total_linea(self):
        return self.cantidad * self.precio_unitario