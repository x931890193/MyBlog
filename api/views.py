# Create your views here.

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import ChinesePoems, PoemsAuthors, PoetryAuthors, AddressInfo, ChineseUniversity
from .models import ChinesePoetry
from .serializers import PoemsSerializer, PoemsAuthorsSerializer, PoetryAuthorsSerializer, AreaSerializer, \
    SubAreaSerializer, PoetryIndexSerializer, ChineseUniversitySerializer
from .serializers import PoetrySerializer


class ChinesePoemsViewSet(ModelViewSet):
    """
    诗; 韵文; 诗一样的作品; 富有诗意的东西;
    """
    serializer_class = PoemsSerializer
    queryset = ChinesePoems.objects.all()


class PoemsAuthorsViewSet(ModelViewSet):
    """
     诗，诗歌; 诗意，诗情; 作诗; 诗歌艺术;
    """
    serializer_class = PoemsAuthorsSerializer
    queryset = PoemsAuthors.objects.all()


class ChinesePoetryViewSet(ModelViewSet):
    serializer_class = PoetrySerializer
    queryset = ChinesePoetry.objects.all()


class PoetryAuthorsViewSet(ModelViewSet):
    serializer_class = PoetryAuthorsSerializer
    queryset = PoetryAuthors.objects.all()


class AreasViewSet(ReadOnlyModelViewSet):
    """
    行政区划信息
    """
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        """
        提供数据集
        """
        if self.action == 'list':
            return AddressInfo.objects.filter(parent=None)
        else:
            return AddressInfo.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer


from drf_haystack.viewsets import HaystackViewSet


class PoetrySearchViewSet(HaystackViewSet):
    """
    诗，诗歌; 诗意，诗情; 作诗; 诗歌艺术;
          This article is about the art form. For other uses, see Poetry (disambiguation)."Poem", "Poems", and "Poetic" redirect here. For other uses, see Poem (disambiguation), Poems (disambiguation), and Poetic (disambiguation).
The Parnassus (1511) by Raphael: famous poets recite alongside the nine Muses atop Mount Parnassus.Poetry (the termderives from a variant of the Greek term, poiesis, "making") is a form of literature that uses aesthetic and rhythmic qualities of language—such as phonaesthetics, sound symbolism, and metre—to evoke meanings in addition to, or in place of, the prosaic ostensible meaning.
    """
    index_models = [ChinesePoetry]

    serializer_class = PoetryIndexSerializer


class ChineseUniversityViewSet(ModelViewSet):
    queryset = ChineseUniversity.objects.all()
    serializer_class = ChineseUniversitySerializer
