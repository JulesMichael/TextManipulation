import unittest
from TextManipulation import groupWords
from TextManipulation import serializer
from TextManipulation import get_page_text

class TestSerializerAndBases(unittest.TestCase):

    def test_groupWords_by2(self):
        serialized_text = serializer("Bonjour je test mon script.")
        gw = groupWords(serialized_text,2)
        self.assertEqual(gw, [['Bonjour', 'je'], ['je', 'test'], ['test', 'mon'],['mon','script']])
        
    def test_groupWords_by3(self):
        serialized_text = serializer("Bonjour je test mon script.")
        gw = groupWords(serialized_text,3)
        self.assertEqual(gw, [['Bonjour', 'je', 'test'], ['je', 'test', 'mon'], ['test', 'mon', 'script']])
    
    def test_get_page_text(self):
        text = get_page_text("http://www.python.org/")
        self.assertEqual(type(text),str)
        
    def test_get_page_text_fail(self):
        text = get_page_text("http://www.python.org_/")
        self.assertEqual(text,None)

if __name__ == '__main__':
    unittest.main()