Attribute VB_Name = "Model_Script"
Option Explicit

Sub Main()
  Call Floors_and_Columns
  Call UFPs
  Call Formatting
End Sub

Sub Floors_and_Columns()
  
  'Create new sheets
  Call Make_New_Sheet("nodes", "NodeUID", "Tag", "X", "Y", "Z", "Group")
  Call Make_New_Sheet("nodeFix", "NodeID", "X", "Y", "Z", "MX", "MY", "MZ")
  Call Make_New_Sheet("diaphragms", "ConstrainedNode", "RetainedNode")
  Call Make_New_Sheet("nodeMass", "NodeUID", "X", "Y", "Z", "MX", "MY", "MZ")
  Call Make_New_Sheet("elements", "Element", "Tag", "Type", "iNode", "jNode", "PropertyID", "Transformation", "Group")
  
  'Loop through all floors
  Dim rng As Range
  Dim N As Long
  Dim floorName As String
  Dim lastFloorName As String
  N = FloorPlan.Range("Floor_Plan_Center_Table").Rows.Count
  Dim iFloor As Integer
  Dim target As Worksheet
  Set target = Sheets("nodes")
  Dim nodeName As String
  Dim centerNodeName As String
  For iFloor = 1 To N Step 1
    floorName = Range("Floor_Plan_Center_Table").Cells(iFloor, 1).Value
    centerNodeName = floorName & "_center"
    'First, add diaphragm nodes to each floor except the first
    If iFloor <> 1 Then
      Call Add_Node(centerNodeName, _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 3).Value, _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 4).Value, _
        "=VLOOKUP(VLOOKUP(""" & floorName & """,Floor_Plan_Center_Table,2,FALSE),Grid,2,FALSE)", _
        "floor mass")
      Call Add_Fixed_Node(centerNodeName, "Diaphragm")
      Call Add_Nodal_Mass(centerNodeName, _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 5), _
        Range("Floor_Plan_Center_Table").Cells(iFloor, 6))
    End If
    
    'Second: Add every node on floor to the list of nodes.
    Dim row As Range
    For Each row In Range("Floor_Plan_Node_Table").Rows
      'Create node. Pass over nodes that do not exist on ground floor.
      nodeName = floorName & row.Cells(1).Value
      If iFloor <> 1 Or row.Cells(5).Value <> "None" Then
        Call Add_Node( _
          floorName & row.Cells(1).Value, _
          "=VLOOKUP(""" & row.Cells(2).Value & """,Grid,2,FALSE)", _
          "=VLOOKUP(""" & row.Cells(3).Value & """,Grid,2,FALSE)", _
          "=VLOOKUP(VLOOKUP(""" & floorName & """,Floor_Plan_Center_Table,2,FALSE),Grid,2,FALSE)", _
          floorName, row.Cells(1, 6).Value)
      End If
      
      'Create supports on ground floor
      If iFloor = 1 And row.Cells(1, 5).Value <> "None" Then
        Call Add_Fixed_Node(nodeName, fixity:=row.Cells(1, 5).Value)
        'Add "support" to node group
        Call Add_Group_Tag(Sheets("nodes").Cells(Next_Row("nodes") - 1, 6), "base support")
        
      'Add nodes to diaphragm constraints.
      ElseIf iFloor <> 1 And row.Cells(4) Then
        Call Add_Diaphragm_Constraint(nodeName, centerNodeName)
      End If
      
    Next row
    
    'Third: Add every floor element to the list of elements
    If iFloor <> 1 Then
      For Each row In Range("Floor_Plan_Elements_Horiz").Rows
        Call Add_Element(floorName & row.Cells(1), _
          row.Cells(2), _
          floorName & row.Cells(3), _
          floorName & row.Cells(4), _
          row.Cells(5), _
          row.Cells(6))
      Next row
    'Fourth: Add interstory elements (columns and walls)
    
      For Each row In Range("Floor_Plan_Elements_Vert").Rows
        Call Add_Element(floorName & row.Cells(1), _
          row.Cells(2), _
          lastFloorName & row.Cells(3), _
          floorName & row.Cells(3), _
          row.Cells(4), _
          row.Cells(5))
      Next row
    End If
    lastFloorName = floorName
  Next iFloor
  
  'Fifth: Add elements that extend above roof.
  floorName = "Top"
  Dim node As String, xGrid As String, yGrid As String
  For Each row In Range("Floor_Plan_Elements_Vert").Rows
    If row.Cells(6).Value Then
      node = row.Cells(3).Value
      xGrid = WorksheetFunction.VLookup(node, Range("Floor_Plan_Node_Table"), 2, False)
      yGrid = WorksheetFunction.VLookup(node, Range("Floor_Plan_Node_Table"), 3, False)
      Debug.Print node, xGrid, yGrid
      Call Add_Node(floorName & row.Cells(3), _
                    "=VLOOKUP(""" & xGrid & """,Grid,2,FALSE)", _
                    "=VLOOKUP(""" & yGrid & """,Grid,2,FALSE)", _
                    "=VLOOKUP(""Level 10.1"",Grid,2,FALSE)", _
                    "main; wall")
      Call Add_Element(floorName & row.Cells(1), _
                       row.Cells(2), _
                       lastFloorName & row.Cells(3), _
                       floorName & row.Cells(3), _
                       row.Cells(4), _
                       row.Cells(5))
    End If
  Next row
End Sub

Sub UFPs()
  Dim row As Range
  Dim wall As String, iCol As String, jCol As String, h As Double
  For Each row In Range("UFP_Table").Rows
    wall = row.Cells(1)
    iCol = row.Cells(2)
    jCol = row.Cells(3)
    h = row.Cells(4)
    
    'Names of elements to cut
    Dim wallNode As String, iNode As String, jNode As String
    wall = Find_Vertical_Element(wall, h)
    iCol = Find_Vertical_Element(iCol, h)
    jCol = Find_Vertical_Element(jCol, h)
    
    'Cut each at specified height
    Dim L As Double, nodeZ As Double
    nodeZ = Get_Table_Property("nodes", wall, "Z")
    L = h - nodeZ
    
    Call Cut_Element(wallNode, L, "UFP")
    Call Cut_Element(iNode, L, "UFP")
    Call Cut_Element(jNode, L, "UFP")
    
    
    'Add UFP between wall and iCol
    
    'Add UFP between wall and jCol
    
  Next row
  
  
  
  
  
  
  
  

End Sub

Sub Formatting()
  Sheets("nodes").Columns(6).AutoFit
  Sheets("diaphragms").Range("A:B").ColumnWidth = 20
  Sheets("elements").Columns("A").AutoFit
  Sheets("elements").Columns("C").ColumnWidth = 18.5
  Sheets("elements").Columns("F:G").ColumnWidth = 13.8
  Sheets("elements").Columns("H").AutoFit
End Sub
