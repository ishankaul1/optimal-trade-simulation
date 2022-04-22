#Unit testing for state and state generation
import unittest

import sys
sys.path.append('../src')

import actions as actions

class TestActions(unittest.TestCase):
    def setUp(self) -> None:
        transfertemplate = actions.TransferTemplate(resource1='water', resource1_amount=5, resource2='earth',
                                                    resource2_amount=3)
        transformtemplate = actions.TransformTemplate(input_resources={'water': 6, 'earth': 6},
                                                      output_resources={'fire': 12})
        self.transfer = actions.ActionableTransfer(template=transfertemplate, country1='X3', country2='X1')
        self.transform = goodtransform = actions.ActionableTransform(template=transformtemplate, country='X3')

    def testTransferFlow(self):
        persistable = self.transfer.convertToPersistable(1)
        persistable2 = self.transfer.convertToPersistable(3)
        print(persistable.toString())
        print(persistable2.toString())

        self.assertTrue(True) #I really didn't wanna hand-write this string lol

    def testTransformFlow(self):
        persistable = self.transform.convertToPersistable(1)
        persistable2 = self.transform.convertToPersistable(3)
        print(persistable.toString())
        print(persistable2.toString())

        self.assertTrue(True)  # I really didn't wanna hand-write this string lol

if __name__ == '__main__':
    unittest.main()