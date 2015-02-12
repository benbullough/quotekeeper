from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from quotes.models import Quote
from quotes.models import Tag


class QuoteTestCase(TestCase):

    def setUp(self):
        """
            Runs before all tests
        """
        test_usr = User.objects.create_user('test', 'test@example.com', 'password')
        q1 = Quote.objects.create(text="I am a rock.  I am an island.", author="Simon & Garfunkel", source="I Am A Rock", date_added=timezone.now(), order=1, user=test_usr)
        q2 = Quote.objects.create(text="Second quote", author="Ben", source="rumor", date_added=timezone.now(), order=1, user=test_usr)
        tag1 = Tag.objects.create(name='Tag1')
        tag2 = Tag.objects.create(name='Tag2')
        q1.tags.add(tag1)
        q1.tags.add(tag2)
        q2.tags.add(tag1)

        test_usr2 = User.objects.create_user('test2', 'test2@example.com', 'password2')
        q3 = Quote.objects.create(text="Third Quote", author="John", source="a little bird told me", date_added=timezone.now(), order=1, user=test_usr2)
        tag3 = Tag.objects.create(name='Tag3')
        q3.tags.add(tag1)
        q3.tags.add(tag3)

    def test_quote_get_by_username(self):
        """
            Test that only quotes for the correct user are returned
        """
        quote_list = Quote.objects.filter(user=User.objects.get(username='test'))
        self.assertEqual(len(quote_list), 2)
        self.assertEqual(quote_list[0].user.username, 'test')
    
    def test_quote_remove_tags_not_in_list(self):
        """
            Test that calling the remove_tags_not_in_list function actually removes a tag 
        """
        quote_list = Quote.objects.filter(user=User.objects.get(username='test'), text__contains='rock' )
        self.assertEqual(len(quote_list), 1)
        q1 = quote_list[0]
        self.assertEqual(len(q1.tags.all()), 2)
        q1.remove_tags_not_in_list(['Tag2']) 
        q2 = Quote.objects.get(text="Second quote")        
        self.assertEqual(len(q1.tags.all()), 1)
        self.assertEqual(len(q2.tags.all()), 1)
        
    def test_quote_add_tag_from_string(self):
        """
            Test that the add_tag_from_str function correctly adds a tag to a quotes   
        """
        q1 = Quote.objects.get(pk=1)
        self.assertNotEqual(len(q1.tags.filter(name="Tag1234")), 1)
        q1.add_tag_from_str("Tag1234")
        self.assertEqual(len(q1.tags.filter(name="Tag1234")), 1)
        q2 = Quote.objects.get(pk=2)
        self.assertNotEqual(len(q2.tags.filter(name="Tag1234")), 1)
        q2.add_tag_from_str("Tag1234")
        self.assertEqual(len(q2.tags.filter(name="Tag1234")), 1)

        
if __name__=='__main__':
    unittest.main() 
