from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status


class CustomUpdateModelMixin(mixins.UpdateModelMixin):
    """
    Customized class to update a model instance.
    """
    def custom_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data_to_update = request.data
        for field in args:
            if field not in data_to_update:
                data_to_update[field] = instance.__getattribute__(field)
        serializer = self.get_serializer(instance, data=data_to_update, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
