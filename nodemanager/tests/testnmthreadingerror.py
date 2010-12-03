
import os
import unittest
import nmthreadingerror
import nmrestrictionsprocessor

class TestRestrictionsProcessor(unittest.TestCase):

  def setUp(self):
    self.contentStr = "resource cpu .10\nresource events 100\n"
    self.contentStr2 = "resource cpu .05\nresource events 50\n"
    self.contentArr = ["resource cpu .10\n","resource events 100\n"]
    self.contentArr2 = ["resource cpu .10\n","resource events 50\n"]
    self.filename = "junk_restrictions_file.tmp"
    
    # 'touch' the file
    open(self.filename,"w").close()

  def testread(self):
    # Write out the contents first
    fileo = open(self.filename, "w")
    fileo.write(self.contentStr)
    fileo.close()
    
    # Get the data using read_restrictions_file
    data = nmrestrictionsprocessor.read_restrictions_file(self.filename)
    
    # Check that it is equal to what is expected
    self.assertEqual(self.contentArr, data)
    
  def testwrite(self):
    # Write the data using read_restrictions_file
    data = nmrestrictionsprocessor.write_restrictions_file(self.filename, self.contentArr);

    # Read in the file
    fileo = open(self.filename)
    contents = fileo.read()
    fileo.close()
    
    # Check that it is equal to what is expected
    self.assertEqual(self.contentStr, contents)

  def testupdaterestrictionabsolute(self):
    # Test updating with an absolute value
    contents = nmrestrictionsprocessor.update_restriction(self.contentArr, "resource", "events", "50", func=False)
    self.assertEqual(self.contentArr2, contents)
  
  # Reduce threads to 50
  def _func(self,contents):
    self.assertEqual(contents[0], "resource")
    self.assertEqual(contents[1], "events")
    self.assertEqual(contents[2], "100\n")
    return "50"
      
  def testupdaterestrictionfunction(self):
    # Test updating with a function
    contents = nmrestrictionsprocessor.update_restriction(self.contentArr, "resource", "events", self._func, func=True)
    self.assertEqual(self.contentArr2, contents)
  
  # Reduce CPU to .05 
  def _func2(self,contents):
    self.assertEqual(contents[0], "resource")
    self.assertEqual(contents[1], "cpu")
    self.assertEqual(contents[2], ".10\n")
    return ".05"  
  
  def testprocessrestrictionfile(self):
    # Write out the contents first
    fileo = open(self.filename, "w")
    fileo.write(self.contentStr)
    fileo.close()
    
    task = ("resource", "events", self._func, True)
    task2 = ("resource", "cpu", self._func2, True)
    tasks = [task, task2]
    
    # Tests the process_restriction_file 
    nmrestrictionsprocessor.process_restriction_file(self.filename, tasks)
  
    # Read in the file
    fileo = open(self.filename)
    contents = fileo.read()
    fileo.close()
    
    # Check that it is equal to what is expected
    self.assertEqual(self.contentStr2, contents)
    
  def tearDown(self):
    os.remove(self.filename)


class TestNMThreadingErrorr(unittest.TestCase):

  def setUp(self):
    self.contentStr = "resource cpu .10\nresource events 100\n"
    self.contentStr2 = "resource cpu .10\nresource events 50\n"
    self.contentArr = ["resource cpu .10\n","resource events 100\n"]
    self.contentArr2 = ["resource cpu .10\n","resource events 50\n"]

    self.filename = "resource.v1"
    self.filename2 = "resource.v2"

    # 'touch' the file
    open(self.filename,"w").close()
    open(self.filename2,"w").close()
  
  def testupdate_restrictions(self):
    # Create the two resource files
    fileo = open(self.filename,"w")
    fileo.write(self.contentStr)
    fileo.close()
    fileo = open(self.filename2,"w")
    fileo.write(self.contentStr)
    fileo.close()
    
    # Call into nmthreadingerror
    nmthreadingerror.update_restrictions()
    
    # Check the restriction files
    fileo = open(self.filename)
    contents = fileo.read()
    fileo.close()
    fileo = open(self.filename2)
    contents2 = fileo.read()
    fileo.close()
    
    # Check that it is equal to what is expected
    self.assertEqual(self.contentStr2, contents)
    self.assertEqual(self.contentStr2, contents2)
  
  def testget_allocated_threads(self):
    # Create the two resource files
    fileo = open(self.filename,"w")
    fileo.write(self.contentStr)
    fileo.close()
    fileo = open(self.filename2,"w")
    fileo.write(self.contentStr)
    fileo.close()
    
    # Call into nmthreadingerror
    alloc = nmthreadingerror.get_allocated_threads()
     
    # Check that it is equal to what is expected
    self.assertEqual(alloc, 200)
    
  def tearDown(self):
    os.remove(self.filename)    
    os.remove(self.filename2)  
      
      
if __name__ == '__main__':
    unittest.main()