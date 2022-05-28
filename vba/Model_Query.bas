Attribute VB_Name = "Model_Query"
Option Explicit

Function Get_Node_Coords(nodeName As String) As Variant
'Written 28-May-2022
'Returns array of nodal coordinates
  Dim arr(3) As Variant
  
  arr(0) = Get_Table_Property("nodes", nodeName, "X")
  arr(1) = Get_Table_Property("nodes", nodeName, "Y")
  arr(2) = Get_Table_Property("nodes", nodeName, "Z")
  
  Get_Node_Coords = arr
  
End Function

Function Dist_btwn_Nodes(node1 As String, node2 As String) As Double
  'Written 28-May-2022
  Dim n1 As Variant, n2 As Variant
  n1 = Get_Node_Coords(node1)
  n2 = Get_Node_Coords(node2)
  
  Dist_btwn_Nodes = Sqr((n1(0) - n2(0)) ^ 2 + (n1(1) - n2(1)) ^ 2 + (n1(2) - n2(2)) ^ 2)
  
End Function

Function Get_Table_Property(sh As String, UID As String, colStr As String) As String
'Written 04-Apr-2022
'Works similar to VLOOKUP for a sheet with one data table
  Dim rng As Range
  Set rng = Table_Range(sh)
  Dim iRow As Long, iCol As Long
  iRow = WorksheetFunction.Match(UID, rng.Columns(1), 0)
  iCol = WorksheetFunction.Match(colStr, rng.Rows(1).Offset(-1), 0)
  Get_Table_Property = rng.Cells(iRow, iCol)
End Function
