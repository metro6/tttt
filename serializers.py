class TrainingReadSerializer(serializers.ModelSerializer):
    trainer = TrainerSerializer(read_only=True)
    date = serializers.SerializerMethodField(read_only=True)
    n_date = serializers.SerializerMethodField(read_only=True)
    end_date = serializers.SerializerMethodField(read_only=True)
    n_end_date = serializers.SerializerMethodField(read_only=True)
    place = serializers.SerializerMethodField(read_only=True)
    sport = serializers.SerializerMethodField(read_only=True)
    clients = ClientSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    duration = serializers.SerializerMethodField(read_only=True)
    comment = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Training
        fields = '__all__'

    @staticmethod
    def get_trainer(obj):
        return obj.trainer.pk

    @staticmethod
    def get_date(obj):
        return int(obj.date.timestamp() * 1000)\

    @staticmethod
    def get_n_date(self):
        return self.date

    @staticmethod
    def get_end_date(obj):
        return int(obj.end_date.timestamp() * 1000)

    @staticmethod
    def get_n_end_date(self):
        return self.end_date

    @staticmethod
    def get_place(obj):
        return obj.place.address

    @staticmethod
    def get_sport(obj):
        return obj.sport.name

    @staticmethod
    def get_rating(obj):
        return ClientTraining.objects.filter(training=obj).aggregate(sum=Sum('rating'))['sum']

    @staticmethod
    def get_duration(obj):
        if obj.duration is not None:
            return obj.duration.minutes
        return 0

    @staticmethod
    def get_comment(obj):
        return obj.comment

    @staticmethod
    def get_price(obj):
        if obj.type is 'personal':
            return Price.get_price(obj.sport, 1, obj.max_clients, obj.duration, obj.trainer, obj.type)
        else:
            if obj.price:
                return obj.price
            else:
                return Price.get_price(obj.sport, 1, obj.max_clients, obj.duration, obj.trainer, obj.type)



class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'

    def create(self, validated_data):
        training = Training(**validated_data)
        if isinstance(validated_data['date'], list):
            date = float(validated_data['date'][0])
        else:
            date = float(validated_data['date'])
        try:
            training.date = timezone.datetime.fromtimestamp(date)
        except ValueError:
            training.date = timezone.datetime.fromtimestamp(date / 1000)
        if isinstance(validated_data['end_date'], list):
            end_date = float(validated_data['end_date'][0])
        else:
            end_date = float(validated_data['end_date'])
        try:
            training.end_date = timezone.datetime.fromtimestamp(end_date)
        except ValueError:
            training.end_date = timezone.datetime.fromtimestamp(end_date / 1000)
        training.price = Price.get_price(training.sport, 1, 1, training.duration, training.trainer)
        training.save()
        return training
