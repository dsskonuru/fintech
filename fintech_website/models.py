from django.db import models
# import datetime
# from django.core.validators import MaxValueValidator, MinValueValidator

'''
class CodeSnippet(models.Model):
    qty = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(148366), MinValueValidator(100027)]
     )


class Snippet(models.Model):
    name = models.CharField(max_length=150)
    code = CodeSnippet()
    from_date = models.DateField(default=datetime.datetime.now())
    to_date = models.DateField(default=datetime.datetime.now() - datetime.timedelta(days=365))

    def __str__(self):
        return [self.code, self.name, self.from_date, self.to_date]


'''