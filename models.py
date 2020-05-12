class Training(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE,
                                verbose_name='Тренер')
    date = models.DateTimeField('Дата тренировки')
    end_date = models.DateTimeField('Дата конца тренировки')
    place = models.ForeignKey(TrainingPlace, on_delete=models.SET_NULL,
                              null=True, verbose_name='Место тренировки')
    STATUS_CHOICES = (
        ('scheduled', 'Запланированная'),
        ('completed', 'Проведенная'),
        ('canceled', 'Отмененная')
    )
    status = models.TextField('Статус', default='scheduled',
                              choices=STATUS_CHOICES)
    TYPE_CHOICES = (
        ('personal', 'Персональная'),
        ('group', 'Групповая')
    )
    type = models.TextField('Персональная/Групповая', default='personal',
                            choices=TYPE_CHOICES)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True,
                              verbose_name='Вид спорта')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты',
                                     through='trainings.ClientTraining')
    max_clients = models.PositiveSmallIntegerField(
        default=1, verbose_name='Максимальное количество клиентов')
    price = models.PositiveSmallIntegerField('Стоимость', blank=True)
    duration = models.ForeignKey(TrainingDuration, models.SET_NULL, default=None,
                                 null=True, verbose_name='Продолжительность')
    created_by_user = models.BooleanField(default=False, verbose_name='Создано от имени пользователя')
    created_by = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    comment = models.TextField(default='', blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'

    def save(self, *args, **kwargs):
        if not self.price:
            Price = apps.get_model('balance.Price')
            self.price = Price.get_price(self.sport, 1, 1, self.duration, self.trainer, self.type)

        super().save(*args, **kwargs)

    def clean(self):
        trainings = Training.objects.\
            filter(trainer=self.trainer).\
            filter(
                Q(date__gte=self.date, date__lte=self.end_date) |
                Q(end_date__gte=self.date, end_date__lte=self.end_date)
            )
        if trainings.count() > 0:
            if trainings.count() > 1 or trainings.first().pk != self.pk:
                raise ValidationError('Возникло пересечение по времени тренировок для тренера ' + self.trainer.name)

    def __str__(self):
        return '{}/{}/{}/{}'.format(self.id, self.trainer, self.sport, self.place)

    @property
    def rating(self):
        result = ClientTraining.objects.filter(training=self).aggregate(
            rating_avg=Avg('rating'))['rating_avg']
        if result is None:
            return None
        return "{0:.2f}".format(result)
    rating.fget.short_description = 'Общая оценка'


class ClientTraining(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               verbose_name='Клиент')
    training = models.ForeignKey(Training, on_delete=models.CASCADE,
                                 verbose_name='Тренировка')
    rating = models.SmallIntegerField(default=0, verbose_name='Оценка')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыта?')

    class Meta:
        verbose_name = 'Забронированная тренировка'
        verbose_name_plural = 'Забронированные тренировки'

    def __str__(self):
        return '{} - {}'.format(self.client, self.training)

