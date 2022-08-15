Attribute VB_Name = "Model_Script"
Option Explicit

Sub Main()
  Call Floors_and_Columns
  Call UFPs
  Call PTs
  Call MultiSpring
  Call Formatting
End Sub

Sub Floors_and_Columns()
  
  'Create new sheets
  Call Make_New_Sheet("nodes", "NodeUID", "Tag", "X", "Y", "Z", "Group")
  Call Make_New_Sheet("nodeFix", "NodeID", "X", "Y", "Z", "MX", "MY", "MZ")
  Call Make_New_Sheet("diaphragms", "ConstrainedNode", "RetainedNode")
  Call Make_New_Sheet("nodeMass", "NodeUID", "X", "Y", "Z", "MX", "MY", "MZ")
  Call Make_New_Sheet("elements", "Element", "Tag", "Type", "iNode", "jNode", "PropertyID", "Transformation", "Group")
  
  Sheets("nodes").Tab.ColorIndex = 3
  Sheets("nodeFix").Tab.ColorIndex = 3
  Sheets("diaphragms").Tab.ColorIndex = 3
  Sheets("nodeMass").Tab.ColorIndex = 3
  Sheets("elements").Tab.ColorIndex = 3
  
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
          row.Cells(6), _
          row.Cells(7))
      Next row
    'Fourth: Add interstory elements (columns and walls)
    
      For Each row In Range("Floor_Plan_Elements_Vert").Rows
        Call Add_Element(floorName & row.Cells(1), _
          row.Cells(2), _
          lastFloorName & row.Cells(3), _
          floorName & row.Cells(3), _
          row.Cells(4), _
          row.Cells(5), _
          row.Cells(6))
      Next row
    End If
    lastFloorName = floorName
  Next iFloor
  
  'Fifth: Add elements that extend above roof.
  floorName = "Top"
  Dim node As String, xGrid As String, yGrid As String
  For Each row In Range("Floor_Plan_Elements_Vert").Rows
    If row.Cells(7).Value Then
      node = row.Cells(3).Value
      xGrid = WorksheetFunction.VLookup(node, Range("Floor_Plan_Node_Table"), 2, False)
      yGrid = WorksheetFunction.VLookup(node, Range("Floor_Plan_Node_Table"), 3, False)
      'Debug.Print node, xGrid, yGrid
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
  Dim name As String, wall As String, iCol As String, jCol As String, h As Double, property As String
  For Each row In Range("UFP_Table").Rows
    name = row.Cells(1)
    wall = row.Cells(2)
    iCol = row.Cells(3)
    jCol = row.Cells(4)
    h = row.Cells(5)
    property = row.Cells(6)
    
    'Names of elements to cut
    Dim wallNode As String, iNode As String, jNode As String
    wall = Find_Vertical_Element(wall, h)
    iCol = Find_Vertical_Element(iCol, h)
    jCol = Find_Vertical_Element(jCol, h)
    
    'Cut each at specified height
    Dim L As Double, nodeZ As Double
    
    nodeZ = Get_Table_Property("nodes", Get_Table_Property("elements", wall, "iNode"), "Z")
    L = h - nodeZ
    Call Cut_Element(wall, L, "UFP")
    Call Cut_Element(iCol, L, "UFP")
    Call Cut_Element(jCol, L, "UFP")
    
    'New node names
    wall = wall & "_UFP"
    iCol = iCol & "_UFP"
    jCol = jCol & "_UFP"
    
    'Add UFP between wall and iCol
    L = Dist_btwn_Nodes(wall, iCol)
    L = L - 10.3125 'All UFPs are same distance from column centerline
    Call Add_UFP(name & "_L", wall, iCol, property, L)
    
    'Add UFP between wall and jCol
    L = Dist_btwn_Nodes(wall, jCol)
    L = L - 10.3125 'All UFPs are same distance from column centerline
    Call Add_UFP(name & "_R", wall, jCol, property, L)
    
  Next row
  
End Sub

Sub PTs()
  
  'Variable Declarations
  Dim row As Range
  Dim coord As Variant
  Dim x As Double, y As Double, z_top As Double, z_bottom As Double
  Dim name As String
  
  'Loop through each vertical PT bar
  For Each row In Range("PT_Table").Rows
    name = row.Cells(1)
    coord = Get_Node_Coords(row.Cells(2))
    'Offset PT node from top of wall
    x = coord(0) + row.Cells(4)
    y = coord(1) + row.Cells(5)
    z_top = coord(2) + row.Cells(6)
    z_bottom = row.Cells(7)
    
    'Make top and bottom nodes
    Call Add_Node(name & "_top", CStr(x), CStr(y), CStr(z_top), "PT")
    Call Add_Node(name & "_base", CStr(x), CStr(y), CStr(z_bottom), "PT")
    Call Add_Fixed_Node(name & "_base", "Fixed")
    Call Add_Element(name & "_link", "rigidLink", row.Cells(2), name & "_top", "", "", "PT_link")
    
    
    'Make elements. Split if two diameters.
    If row.Cells(8) Then 'Two PT diameters
      Dim z_split As Double
      z_split = row.Cells(9)
      Call Add_Node(name & "_split", CStr(x), CStr(y), CStr(z_split), "PT")
      Call Add_Fixed_Node(name & "_split", "Truss")
      Call Add_Element(name & "_lower", "PT", name & "_base", name & "_split", row.Cells(3), "", "PT")
      Call Add_Element(name, "PT", name & "_split", name & "_top", row.Cells(10), "", "PT")
    Else 'One uniform bar
      Call Add_Element(name, "PT", name & "_base", name & "_top", row.Cells(3), "", "PT")
    End If
  Next row
  
End Sub

Sub MultiSpring()
  '10-Aug-2022
  'Generates Winkler Spring Analogy style nodes and elements at base of walls
  
  'Variable Declarations
  Dim shNodes As Worksheet, shWeights As Worksheet
  Dim row As Range
  Dim coord As Variant
  Dim Lx As Double, Ly As Double, Nx As Double, Ny As Double, area As Double, K As Double, E As Double, Leff As Double
  Dim name As String, mainNode As String, springProperty As String, nameIJ As String
  Dim dx As Double, dy As Double
  Dim nodesX As Range, nodesY As Range
  Dim weightsX As Range, weightsY As Range
  Dim xCol As Long, yCol As Long
  
  'Create/reset multisping sheet.
  Call Make_New_Sheet("multispring", "ElementUID", "Area", "K")
  
  Sheets("multispring").Tab.ColorIndex = 3
  
  'Loop through each wall base
  For Each row In Range("Base_Spring_Table").Rows
    '1 - Read table.
    name = row.Cells(1)
    mainNode = row.Cells(2)
    springProperty = row.Cells(3)
    Lx = row.Cells(4)
    Nx = row.Cells(5)
    Ly = row.Cells(6)
    Ny = row.Cells(7)
    
    'Integration information
    Set shNodes = Sheets("integration_nodes")
    Set shWeights = Sheets("integration_weights")
    xCol = WorksheetFunction.Match(Nx, shNodes.Range("1:1"), 0)
    yCol = WorksheetFunction.Match(Ny, shNodes.Range("1:1"), 0)
    
    Set nodesX = Range(shNodes.Cells(2, xCol), shNodes.Cells(2, xCol).Offset(Nx + 1, 0))
    Set nodesY = Range(shNodes.Cells(2, yCol), shNodes.Cells(2, yCol).Offset(Ny + 1, 0))
    Set weightsX = Range(shWeights.Cells(2, xCol), shWeights.Cells(2, xCol).Offset(Nx + 1, 0))
    Set weightsY = Range(shWeights.Cells(2, yCol), shWeights.Cells(2, yCol).Offset(Ny + 1, 0))
    
    '2 - Remove fixity for base node.
    Call Remove_Row("nodeFix", Get_Table_Row("nodeFix", mainNode) + 1) 'Add one to compensate for header row.
    'Debug.Print mainNode, Get_Table_Row("nodeFix", mainNode)
    
    '3 - Get coordinates of base node.
    coord = Get_Node_Coords(row.Cells(2))
    
    '4 - Add Nx*Ny elements. Start by creating new nodes.
    Dim i As Long, j As Long
    For i = 1 To Nx
    For j = 1 To Ny
      nameIJ = name & "_" & CStr(i) & "_" & CStr(j)
      
      '5 - Fixed node.
      dx = Lx / 2 * nodesX.Cells(i)
      dy = Ly / 2 * nodesY.Cells(j)
      area = Lx / 2 * Ly / 2 * weightsX.Cells(i) * weightsY.Cells(j)
      
      Call Add_Node(nameIJ & "_fixed", CStr(coord(0)) + dx, CStr(coord(1)) + dy, CStr(coord(2)), "base")
      Call Add_Fixed_Node(nameIJ & "_fixed", "Fixed")
      
      '6 - Free node. Connect it to the main node.
      Call Add_Node(nameIJ & "_free", CStr(coord(0)) + dx, CStr(coord(1)) + dy, CStr(coord(2)), "base")
      Call Add_Element(nameIJ & "_link", "rigidLink", mainNode, nameIJ & "_free", springProperty, "", "base_link")
      
      '7 - Create an element between the two nodes.
      Call Add_Element(nameIJ, "multiSpring", mainNode, nameIJ & "_free", springProperty, "", "base")
      
      '8 - Add element to multisping sheet.
      E = Get_Table_Property("eleProperties", springProperty, "E")
      Leff = Get_Table_Property("eleProperties", springProperty, "Leff")
      K = area * E / Leff
      Call Add_Row_to_Sheet("multispring", nameIJ, area, K)
    
    Next j
    Next i
    
  Next row
  
  Sheets("multispring").Columns("A").AutoFit
  
End Sub

Sub Formatting()

  Sheets("nodes").Columns(1).AutoFit
  Sheets("nodes").Columns(6).AutoFit
  
  Sheets("nodeFix").Columns(1).AutoFit
  Sheets("nodeMass").Columns(1).AutoFit
  
  Sheets("diaphragms").Range("A:B").ColumnWidth = 20
  
  Sheets("elements").Columns("A").AutoFit
  Sheets("elements").Columns("C").ColumnWidth = 18.5
  Sheets("elements").Columns("F:G").ColumnWidth = 13.8
  Sheets("elements").Columns("H").AutoFit
  
End Sub

