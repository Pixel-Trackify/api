from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .schema import custom_token_verify_schema
from goals.models import Goal


User = get_user_model()


@custom_token_verify_schema
class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            token = UntypedToken(request.data['token'])

            # Decodificar o token para obter os dados do usuário
            user_uid = token['user_uid']
            user = User.objects.get(uid=user_uid)

            # Obter o profit do usuário
            fup = user_profit = user.profit
            if user_profit < 0:
                fup = 0
                
            # Determinar a regra da meta com base no range de faturamento
            goal_rule = Goal.objects.filter(
                min__lte=fup, max__gte=user_profit).first()

            # Construir o objeto goals com min e max
            goals_data = {
                "min": goal_rule.min if goal_rule else None,
                "max": goal_rule.max if goal_rule else None,
            }

            return Response({
                "message": "Token is valid",
                "user": {
                    "uid": user.uid,
                    "name": user.name,
                    "email": user.email,
                    "avatar": user.avatar,
                    "role": "admin" if user.is_superuser else "user",
                    "profit": user_profit,
                    "goals": goals_data,
                }
            }, status=status.HTTP_200_OK)
        except (InvalidToken, TokenError) as e:
            return Response({
                "message": "Token is invalid or expired",
                "detail": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                "message": "User not found",
                "detail": "No user matching this token was found."
            }, status=status.HTTP_404_NOT_FOUND)
