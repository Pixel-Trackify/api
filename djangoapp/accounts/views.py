import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from accounts.models import Accounts

# Create your views here.

@csrf_exempt
def account_create_list_view(request):
    if request.method == 'GET':
        account = Accounts.objects.all()
        data = [{'id': account.id,'name': account.name, 'email': account.email, 'cpf': account.cpf} for account in account] #serializers (manual)
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        new_account = Accounts(name=data['name'], email=data['email'], cpf=data['cpf'])
        new_account.save()
        return JsonResponse(
            {'id': new_account.id, 'name': new_account.name, 'email': new_account.email, 'cpf': new_account.cpf},
            status=201,
        )
    

@csrf_exempt
def account_detail_view(request, pk):
    account = get_object_or_404(Accounts, pk=pk)

    if request.method == 'GET':
        data = {'id': account.id,'name': account.name, 'email': account.email, 'cpf': account.cpf}
        return JsonResponse(data)

    elif request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        account.name = data['name']
        account.email = data['email']
        account.cpf = data['cpf']
        account.save()
        return JsonResponse(
            {'id': account.id, 'name': account.name, 'email': account.email, 'cpf': account.cpf},
            status=201,
        )
    
    elif request.method == 'DELETE':
        account.delete()
        return JsonResponse(
            {'message': 'Genero excluido com sucesso'},
            status=204,
        )
    
        
