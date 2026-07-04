package com.example.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(viewModel: MainViewModel) {
    var selectedTab by remember { mutableIntStateOf(0) }
    val scope = rememberCoroutineScope()

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.School,
                            contentDescription = "School Logo",
                            tint = Color(0xFF059669),
                            modifier = Modifier.size(32.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = "Greenwood School",
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1E3A8A)
                            )
                            Text(
                                text = "ERP Admissions Assistant",
                                fontSize = 11.sp,
                                color = Color.Gray
                            )
                        }
                    }
                },
                actions = {
                    if (selectedTab == 0) {
                        IconButton(
                            onClick = { viewModel.clearHistory() },
                            modifier = Modifier.testTag("clear_chat_button")
                        ) {
                            Icon(Icons.Default.DeleteSweep, contentDescription = "Clear Chat", tint = Color(0xFFE11D48))
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.White,
                    titleContentColor = Color(0xFF1E3A8A)
                )
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = Color.White,
                tonalElevation = 4.dp
            ) {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Icon(Icons.Default.Forum, contentDescription = "Chat") },
                    label = { Text("ERP Chat") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color(0xFF1E3A8A),
                        selectedTextColor = Color(0xFF1E3A8A),
                        indicatorColor = Color(0xFFE2E8F0)
                    )
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Icon(Icons.Default.Storage, contentDescription = "Explorer") },
                    label = { Text("ERP Tables") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color(0xFF1E3A8A),
                        selectedTextColor = Color(0xFF1E3A8A),
                        indicatorColor = Color(0xFFE2E8F0)
                    )
                )
                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    icon = { Icon(Icons.Default.Event, contentDescription = "Campus Visits") },
                    label = { Text("Visits") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color(0xFF1E3A8A),
                        selectedTextColor = Color(0xFF1E3A8A),
                        indicatorColor = Color(0xFFE2E8F0)
                    )
                )
                NavigationBarItem(
                    selected = selectedTab == 3,
                    onClick = { selectedTab = 3 },
                    icon = { Icon(Icons.Default.Info, contentDescription = "Admissions Info") },
                    label = { Text("Admissions Info") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color(0xFF1E3A8A),
                        selectedTextColor = Color(0xFF1E3A8A),
                        indicatorColor = Color(0xFFE2E8F0)
                    )
                )
            }
        },
        containerColor = Color(0xFFF8FAFC)
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when (selectedTab) {
                0 -> ChatTab(viewModel)
                1 -> ExplorerTab(viewModel)
                2 -> VisitsTab(viewModel)
                3 -> InfoTab(viewModel)
            }
        }
    }
}

@Composable
fun ChatTab(viewModel: MainViewModel) {
    val chats by viewModel.chatHistory.collectAsState()
    val isSending by viewModel.isSending.collectAsState()
    var inputText by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()
    val listState = rememberLazyListState()
    val focusManager = LocalFocusManager.current

    LaunchedEffect(chats.size) {
        if (chats.isNotEmpty()) {
            listState.animateScrollToItem(chats.size - 1)
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        if (chats.isEmpty()) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(24.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = Icons.Default.ChatBubbleOutline,
                        contentDescription = "Empty",
                        tint = Color.LightGray,
                        modifier = Modifier.size(80.dp)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No messages yet",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.Gray
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Ask about admission rules, deadlines, fees, or bus routes.",
                        fontSize = 14.sp,
                        color = Color.LightGray,
                        textAlign = TextAlign.Center
                    )
                }
            }
        } else {
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(chats) { msg ->
                    val isUser = msg.role == "user"
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
                    ) {
                        if (!isUser) {
                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(CircleShape)
                                    .background(Color(0xFFE2E8F0)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.Face, contentDescription = "Bot", tint = Color(0xFF1E3A8A), modifier = Modifier.size(18.dp))
                            }
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        
                        Card(
                            colors = CardDefaults.cardColors(
                                containerColor = if (isUser) Color(0xFF1E3A8A) else Color.White
                            ),
                            shape = RoundedCornerShape(
                                topStart = 16.dp,
                                topEnd = 16.dp,
                                bottomStart = if (isUser) 16.dp else 0.dp,
                                bottomEnd = if (isUser) 0.dp else 16.dp
                            ),
                            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
                            modifier = Modifier.widthIn(max = 280.dp)
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Text(
                                    text = msg.content,
                                    color = if (isUser) Color.White else Color.Black,
                                    fontSize = 14.sp
                                )
                            }
                        }
                        
                        if (isUser) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(CircleShape)
                                    .background(Color(0xFFE2E8F0)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Default.Person, contentDescription = "User", tint = Color(0xFF059669), modifier = Modifier.size(18.dp))
                            }
                        }
                    }
                }
                
                if (isSending) {
                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(8.dp),
                            horizontalArrangement = Arrangement.Start
                        ) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                strokeWidth = 2.dp,
                                color = Color(0xFF1E3A8A)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Greenwood BOT is formulating response...", fontSize = 12.sp, color = Color.Gray)
                        }
                    }
                }
            }
        }

        // Input Bar
        Surface(
            tonalElevation = 2.dp,
            color = Color.White,
            modifier = Modifier.fillMaxWidth()
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    placeholder = { Text("Ask Admissions Desk...") },
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = Color(0xFFF1F5F9),
                        unfocusedContainerColor = Color(0xFFF1F5F9),
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    ),
                    shape = RoundedCornerShape(24.dp),
                    modifier = Modifier
                        .weight(1f)
                        .testTag("chat_text_input")
                        .heightIn(min = 48.dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Text)
                )
                Spacer(modifier = Modifier.width(8.dp))
                FloatingActionButton(
                    onClick = {
                        if (inputText.isNotBlank() && !isSending) {
                            viewModel.sendEnquiry(inputText)
                            inputText = ""
                            focusManager.clearFocus()
                        }
                    },
                    containerColor = Color(0xFF1E3A8A),
                    contentColor = Color.White,
                    shape = CircleShape,
                    modifier = Modifier
                        .size(48.dp)
                        .testTag("send_chat_button")
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Send", modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}

@Composable
fun ExplorerTab(viewModel: MainViewModel) {
    val fees by viewModel.fees.collectAsState()
    val routes by viewModel.routes.collectAsState()
    val faqs by viewModel.faqs.collectAsState()
    var subTab by remember { mutableStateOf(0) } // 0=Fees, 1=Routes, 2=FAQs

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = { subTab = 0 },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (subTab == 0) Color(0xFF1E3A8A) else Color(0xFFE2E8F0),
                    contentColor = if (subTab == 0) Color.White else Color(0xFF1E3A8A)
                ),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier.weight(1f).height(40.dp)
            ) {
                Text("Fees", fontSize = 12.sp)
            }
            Button(
                onClick = { subTab = 1 },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (subTab == 1) Color(0xFF1E3A8A) else Color(0xFFE2E8F0),
                    contentColor = if (subTab == 1) Color.White else Color(0xFF1E3A8A)
                ),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier.weight(1f).height(40.dp)
            ) {
                Text("Routes", fontSize = 12.sp)
            }
            Button(
                onClick = { subTab = 2 },
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (subTab == 2) Color(0xFF1E3A8A) else Color(0xFFE2E8F0),
                    contentColor = if (subTab == 2) Color.White else Color(0xFF1E3A8A)
                ),
                shape = RoundedCornerShape(20.dp),
                modifier = Modifier.weight(1f).height(40.dp)
            ) {
                Text("FAQs", fontSize = 12.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            when (subTab) {
                0 -> {
                    items(fees) { f ->
                        Card(
                            colors = CardDefaults.cardColors(containerColor = Color.White),
                            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Text(f.grade, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF1E3A8A))
                                    Text(f.frequency, fontSize = 11.sp, color = Color.Gray)
                                }
                                Divider(modifier = Modifier.padding(vertical = 8.dp), color = Color(0xFFF1F5F9))
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Column {
                                        Text("Registration Fee", fontSize = 11.sp, color = Color.Gray)
                                        Text("$${f.admissionFee}", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                                    }
                                    Column {
                                        Text("Tuition (Term)", fontSize = 11.sp, color = Color.Gray)
                                        Text("$${f.tuitionFeeTerm}", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                                    }
                                    Column {
                                        Text("Caution Deposit", fontSize = 11.sp, color = Color.Gray)
                                        Text("$${f.cautionDeposit}", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                                    }
                                }
                            }
                        }
                    }
                }
                1 -> {
                    items(routes) { r ->
                        Card(
                            colors = CardDefaults.cardColors(containerColor = Color.White),
                            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text(r.routeName, fontWeight = FontWeight.Bold, fontSize = 16.sp, color = Color(0xFF1E3A8A))
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(12.dp))
                                            .background(if (r.status == "Available") Color(0xFFD1FAE5) else Color(0xFFFEE2E2))
                                            .padding(horizontal = 8.dp, vertical = 4.dp),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = r.status,
                                            color = if (r.status == "Available") Color(0xFF065F46) else Color(0xFF991B1B),
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(r.coverageAreas, fontSize = 12.sp, color = Color.Gray)
                                Divider(modifier = Modifier.padding(vertical = 8.dp), color = Color(0xFFF1F5F9))
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text("Driver: ${r.driverName} (${r.driverPhone})", fontSize = 12.sp, color = Color.DarkGray)
                                    Text("$${r.termFee}/term", fontWeight = FontWeight.Bold, fontSize = 14.sp, color = Color(0xFF059669))
                                }
                            }
                        }
                    }
                }
                2 -> {
                    items(faqs) { faq ->
                        Card(
                            colors = CardDefaults.cardColors(containerColor = Color.White),
                            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(faq.question, fontWeight = FontWeight.Bold, fontSize = 14.sp, color = Color(0xFF1E3A8A))
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(faq.answer, fontSize = 13.sp, color = Color.DarkGray)
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = faq.category.uppercase(),
                                    fontSize = 10.sp,
                                    color = Color(0xFF059669),
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun VisitsTab(viewModel: MainViewModel) {
    var pName by remember { mutableStateOf("") }
    var pEmail by remember { mutableStateOf("") }
    var pPhone by remember { mutableStateOf("") }
    var pDate by remember { mutableStateOf("2026-08-10") }
    var pTime by remember { mutableStateOf("09:00 AM - 10:30 AM") }
    var pNotes by remember { mutableStateOf("") }
    
    var showSuccess by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .background(Color.White, shape = RoundedCornerShape(12.dp))
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Schedule Campus Visit", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E3A8A))
        Text("Schedule an interactive, fully guided parent tour of our premium infrastructure.", fontSize = 12.sp, color = Color.Gray)
        
        OutlinedTextField(
            value = pName,
            onValueChange = { pName = it },
            label = { Text("Parent/Guardian Full Name") },
            modifier = Modifier.fillMaxWidth().testTag("visit_name_input"),
            shape = RoundedCornerShape(8.dp)
        )
        OutlinedTextField(
            value = pEmail,
            onValueChange = { pEmail = it },
            label = { Text("Email Address") },
            modifier = Modifier.fillMaxWidth().testTag("visit_email_input"),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            shape = RoundedCornerShape(8.dp)
        )
        OutlinedTextField(
            value = pPhone,
            onValueChange = { pPhone = it },
            label = { Text("Mobile Contact") },
            modifier = Modifier.fillMaxWidth().testTag("visit_phone_input"),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
            shape = RoundedCornerShape(8.dp)
        )
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            OutlinedTextField(
                value = pDate,
                onValueChange = { pDate = it },
                label = { Text("Visit Date") },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp)
            )
            OutlinedTextField(
                value = pTime,
                onValueChange = { pTime = it },
                label = { Text("Slot") },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(8.dp)
            )
        }
        OutlinedTextField(
            value = pNotes,
            onValueChange = { pNotes = it },
            label = { Text("Special Requests or Grades of Interest") },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(8.dp)
        )

        Button(
            onClick = {
                if (pName.isNotBlank() && pEmail.isNotBlank() && pPhone.isNotBlank()) {
                    viewModel.scheduleVisit(pName, pEmail, pPhone, pDate, pTime, pNotes)
                    showSuccess = true
                    pName = ""
                    pEmail = ""
                    pPhone = ""
                    pNotes = ""
                }
            },
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1E3A8A)),
            modifier = Modifier.fillMaxWidth().height(48.dp).testTag("submit_visit_button"),
            shape = RoundedCornerShape(8.dp)
        ) {
            Text("Confirm Booking Request", color = Color.White)
        }

        if (showSuccess) {
            Spacer(modifier = Modifier.height(8.dp))
            Surface(
                color = Color(0xFFD1FAE5),
                contentColor = Color(0xFF065F46),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.CheckCircle, contentDescription = "Success", tint = Color(0xFF059669))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Visit request submitted! Reference booking logged successfully.", fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
fun InfoTab(viewModel: MainViewModel) {
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFEF2F2)),
                border = BorderStroke(1.dp, Color(0xFFFCA5A5)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Warning, contentDescription = "Security Alert", tint = Color(0xFFEF4444))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Security Warning", fontWeight = FontWeight.Bold, color = Color(0xFF991B1B))
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "I have included your API keys in the generated APK file for this prototype. Please be aware that Android APKs can be easily decompiled, and these keys can be extracted by anyone who has access to the file. Do not share this APK file publicly or with unauthorized individuals to prevent potential misuse.",
                        fontSize = 12.sp,
                        color = Color(0xFF7F1D1D)
                    )
                }
            }
        }

        item {
            Text("General Admissions Guidelines", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF1E3A8A))
        }

        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = Color.White),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Age Eligibility Criteria:", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("• Nursery: 3+ Years\n• Kindergarten (KG): 5+ Years\n• Grade 1: 6+ Years\n• Grade 5: 10+ Years\n• Grade 10: 15+ Years", fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Mandatory Verification Documents:", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("• Valid Government Birth Certificate\n• Passport Photos (4 copies)\n• Last 2 academic year scholastic report sheets\n• Transfer Certificate (TC)\n• Aadhaar or Passport ID proof of parents", fontSize = 13.sp)
                }
            }
        }

        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFECFDF5)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Contact Admissions", fontWeight = FontWeight.Bold, fontSize = 14.sp, color = Color(0xFF065F46))
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Email: admissions@greenwoodschool.edu", fontSize = 13.sp, color = Color.DarkGray)
                    Text("Phone: +1-555-0100", fontSize = 13.sp, color = Color.DarkGray)
                    Text("Location: 500 Greenwood Lane, Silicon Valley, CA", fontSize = 13.sp, color = Color.DarkGray)
                }
            }
        }
    }
}
