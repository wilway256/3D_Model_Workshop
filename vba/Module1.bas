Attribute VB_Name = "Module1"
Option Explicit

Function Worksheet_Exists(sheetName As String) As Boolean
Worksheet_Exists = False
Dim i As Integer
  With ThisWorkbook
    For i = 1 To .Sheets.Count
        If .Sheets(i).name = sheetName Then
            Worksheet_Exists = True
            Exit Function
        End If
    Next i
  End With
End Function

Sub Make_New_Sheet(sheetName As String, ParamArray colNames() As Variant)
  Application.DisplayAlerts = False
  'If sheet does not already exist
  If Worksheet_Exists(sheetName) Then
    Sheets(sheetName).Delete
    'To disable warning message, Application.DisplayAlerts = False
  End If
  'Make new sheet
  Worksheets.Add(After:=Sheets(Sheets.Count)).name = sheetName
  Application.DisplayAlerts = True
  'Columns
  Dim i As Integer
  For i = 0 To UBound(colNames())
    Worksheets(sheetName).Cells(1, i + 1).Value = colNames(i)
  Next i
  i = i + 1
  With Sheets(sheetName)
  .Columns(i).Resize(.Rows.Count, .Columns.Count - i + 1).Select
  Selection.EntireColumn.Hidden = True
  End With
End Sub

Function Next_Row(sheetName As String) As Long
  Dim sh As Worksheet
  Set sh = Sheets(sheetName)
  Next_Row = sh.Range("A" & Rows.Count).End(xlUp).Offset(1).row
End Function

Sub Set_Tag(rng As Range)
  Dim tag As Long
  tag = Application.Aggregate(4, 2, rng.EntireColumn) + 1 'Max of column, ignore errors
  rng.Value = tag
End Sub

Sub Add_Group_Tag(rng As Range, tag As String)
'Sets cell value if blank. Appends value with delimiter if not.
  If rng.Value = "" Then
    rng.Value = tag
  Else
    rng.Value = rng.Value & "; " & tag
  End If
End Sub

Sub Add_Node(name As String, x As String, y As String, z As String, ParamArray groupTags() As Variant)
  'Get next empty row
  Dim nextRow As Long
  nextRow = Next_Row("nodes")
  
  With Sheets("nodes")
    'Name Node
    .Cells(nextRow, 1).Value = name
    'Set tag
    Call Set_Tag(.Cells(nextRow, 2))
    'X, Y, and Z
    .Cells(nextRow, 3).Formula = x
    .Cells(nextRow, 3).Value = .Cells(nextRow, 3).Value
    .Cells(nextRow, 4).Formula = y
    .Cells(nextRow, 4).Value = .Cells(nextRow, 4).Value
    .Cells(nextRow, 5).Formula = z
    .Cells(nextRow, 5).Value = .Cells(nextRow, 5).Value
    'Add group tags, if applicable.
    Dim i As Integer
    For i = 0 To UBound(groupTags())
      Call Add_Group_Tag(.Cells(nextRow, 6), CStr(groupTags(i)))
    Next i
  End With
End Sub

Sub Add_Fixed_Node(name As String, fixity As String)
  Dim nextRow As Long
  nextRow = Next_Row("nodeFix")
  'Add node to list of fixed nodes.
  Sheets("nodeFix").Cells(nextRow, 1).Value = name
  'Copy 6 DOF Fixed/Free to nodeFix sheet depending on fixity type.
  Dim i As Double
  i = Application.WorksheetFunction.Match(fixity, Range("Fixity").Columns(1), 0)
  Dim sourceRange As Range
  Set sourceRange = Range(Range("Fixity").Cells(1, 2), Range("Fixity").Cells(Range("Fixity").Rows.Count, 7))
  sourceRange.Rows(i).Copy _
    Destination:=Sheets("nodeFix").Cells(nextRow, 2)
End Sub

Sub Add_Diaphragm_Constraint(constrainedNode As String, retainedNode As String)
  Dim nextRow As Long
  nextRow = Next_Row("diaphragms")
  'Add nodes to diaphragm sheet.
  With Sheets("diaphragms")
    .Cells(nextRow, 1).Value = constrainedNode
    .Cells(nextRow, 2).Value = retainedNode
  End With
End Sub

Sub Add_Nodal_Mass(nodeName As String, latMass As Double, rotMass As Double)
  Dim nextRow As Long
  nextRow = Next_Row("nodeMass")
  'Add nodes to diaphragm sheet.
  With Sheets("nodeMass")
    .Cells(nextRow, 1).Value = nodeName
    .Cells(nextRow, 2).Value = latMass
    .Cells(nextRow, 3).Value = latMass
    .Cells(nextRow, 7).Value = rotMass
    .Range("D" & nextRow & ":F" & nextRow).Value = 0
  End With
End Sub

Sub Add_Element(eleName As String, eleType As String, iNode As String, jnode As String, property As String, transformation As String)
  'eleType refers to the OpenSees element command's first argument. William's cod
  'property referst to another sheet with element properties (A, I, E, etc.)
  Dim nextRow As Long
  nextRow = Next_Row("elements")
  With Sheets("elements")
    .Cells(nextRow, 1).Value = eleName
    Call Set_Tag(.Cells(nextRow, 2))
    .Cells(nextRow, 3).Value = eleType
    .Cells(nextRow, 4).Value = iNode
    .Cells(nextRow, 5).Value = jnode
    .Cells(nextRow, 6).Value = property
    .Cells(nextRow, 7).Value = transformation
  End With
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
  
  'Formatting Tidbits
  Sheets("nodes").Columns(6).AutoFit
  Sheets("diaphragms").Range("A:B").ColumnWidth = 20
  Sheets("elements").Columns("A").AutoFit
  Sheets("elements").Columns("C").ColumnWidth = 18.5
  Sheets("elements").Columns("F:G").ColumnWidth = 13.8
  Sheets("elements").Columns("H").AutoFit
End Sub

Sub Get_Grid_Coord(name As String)
  
End Sub
