from itertools import product
from django.shortcuts import render
from store.models import Product
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator

@never_cache
def home(request):
    products=Product.objects.all().filter(is_available=True)
    product1=[]
    for single_product in products:
        print(single_product)
        product1.append({
            'product_name': single_product.product_name,  
            'slug': single_product.slug,         
            'descrbtion' :single_product.descrbtion,    
            'price'  : single_product.price,       
            'image'  :single_product.image,       
            'stock'  : single_product.stock,       
            'is_available' : single_product.is_available, 
            'category'   :single_product.category,   
            'created_date' :single_product.created_date, 
            'modified_date':single_product.modified_date,
            'offer': (single_product.price-(single_product.category.offer * single_product.price)/100),
             })
    paginator = Paginator(product1, 8)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context={
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request,'home.html',context)