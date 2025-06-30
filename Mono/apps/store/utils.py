from .models import Product, OrderProduct, Order, Customer


class CartAuthenticatedUser:
    def __init__(self, request, product_id=None, action=None):
        self.user = request.user

        if product_id and action:
            self.add_or_delete(product_id, action)

    def get_cart_info(self):
        customer, created = Customer.objects.get_or_create(  # Sotib oluvchini dannilari
            user=self.user
        )
        order, created = Order.objects.get_or_create(customer=customer)  # Kankret sotib olmoqchi boganda ishga tushadi!
        order_products = order.orderproduct_set.all()  # Hamma produktlaga tegishli sotib olishda

        cart_total_quantity = order.get_cart_total_quantity  # produktni obshiy soni obkelindi modeldan
        cart_total_price = order.get_cart_total_price  # produktni obshiy summasi obkelindi modeldan

        return {
            'cart_total_quantity': cart_total_quantity,
            'cart_total_price': cart_total_price,
            'order': order,
            'products': order_products
        }

    def add_or_delete(self, product_id, action):
        order = self.get_cart_info()['order']
        product = Product.objects.get(pk=product_id)
        order_product, created = OrderProduct.objects.get_or_create(order=order, product=product)

        if action == 'add' and product.quantity > 0:
            order_product.quantity += 1
            product.quantity -= 1
        else:
            order_product.quantity -= 1
            product.quantity += 1

        product.save()
        order_product.save()

        if order_product.quantity <= 0:  # Produkt 0 dan tushib ketsa karzina ochib ketsin !
            order_product.delete()

    # Tolov bogandan keyin karzinani tozalab qoyadi !
def clear(self):
    order = self.get_cart_info()['order']
    order_products = order.orderproduct_set.all()
    for product in order_products:
        product.delete()
    order.save()


def get_cart_data(request):
    cart = CartAuthenticatedUser(request)
    cart_info = cart.get_cart_info()


    return {
        'cart_total_quantity': cart_info['cart_total_quantity'],
        'cart_total_price': cart_info['cart_total_price'],
        'order': cart_info['order'],
        'products': cart_info['products']
    }


