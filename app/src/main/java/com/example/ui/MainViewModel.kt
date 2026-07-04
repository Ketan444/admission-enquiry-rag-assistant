package com.example.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.BuildConfig
import com.example.data.*
import com.example.network.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val db = AppDatabase.getDatabase(application)
    private val repository = SchoolRepository(db)

    // UI state
    val chatHistory: StateFlow<List<ChatMsg>> = repository.chatHistory
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val visits: StateFlow<List<CampusVisit>> = repository.visits
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val feedbackList: StateFlow<List<Feedback>> = repository.feedbackList
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private val _isSending = MutableStateFlow(false)
    val isSending: StateFlow<Boolean> = _isSending.asStateFlow()

    // Explorer Data States
    private val _fees = MutableStateFlow<List<FeeStructure>>(emptyList())
    val fees: StateFlow<List<FeeStructure>> = _fees.asStateFlow()

    private val _routes = MutableStateFlow<List<BusRoute>>(emptyList())
    val routes: StateFlow<List<BusRoute>> = _routes.asStateFlow()

    private val _faqs = MutableStateFlow<List<FAQ>>(emptyList())
    val faqs: StateFlow<List<FAQ>> = _faqs.asStateFlow()

    init {
        loadExplorerData()
    }

    fun loadExplorerData() {
        viewModelScope.launch {
            _fees.value = repository.getFeesList()
            _routes.value = repository.getRoutesList()
            _faqs.value = repository.getFAQsList()
        }
    }

    fun clearHistory() {
        viewModelScope.launch {
            repository.clearChatHistory()
        }
    }

    fun sendEnquiry(question: String) {
        if (question.isBlank()) return
        
        viewModelScope.launch {
            _isSending.value = true
            
            // 1. Save user query to persistent ChatMsg history flow
            repository.insertMessage(ChatMsg(role = "user", content = question))
            
            try {
                // 2. Retrieve local grounding context (Android Local RAG!)
                val context = repository.retrieveLocalContext(question)
                
                // 3. Compile history into Gemini Content format
                val currentHistory = chatHistory.value
                val contentsList = mutableListOf<Content>()
                
                // Keep history limited to prevent overflow, but map role correctly
                currentHistory.takeLast(10).forEach { msg ->
                    contentsList.add(
                        Content(parts = listOf(Part(text = msg.content)))
                    )
                }
                
                // 4. Construct system instruction using local context
                val systemInstructionText = """
                    You are the Greenwood School Admission Assistant chatbot. 
                    Ground your responses strictly in the school context below. 
                    Be polite, structural, and welcoming.
                    If details are not in the context, guide the parent to admissions@greenwoodschool.edu.
                    
                    School Context retrieved:
                    $context
                """.trimIndent()

                val request = GenerateContentRequest(
                    contents = contentsList,
                    systemInstruction = Content(parts = listOf(Part(text = systemInstructionText)))
                )

                val apiKey = BuildConfig.GEMINI_API_KEY
                
                if (apiKey.isBlank() || apiKey == "MY_GEMINI_API_KEY" || apiKey == "GEMINI_API_KEY") {
                    // Simulation fallback if key is missing (instruct user clearly)
                    val fallbackResponse = getSimulatedResponse(question, context)
                    repository.insertMessage(
                        ChatMsg(
                            role = "assistant",
                            content = fallbackResponse + "\n\n*(Simulation Mode: Enter your valid GEMINI_API_KEY in the Secrets panel in AI Studio to activate live API grounding.)*"
                        )
                    )
                } else {
                    // Live API Call
                    val response = RetrofitClient.service.generateContent(apiKey, request)
                    val text = response.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text
                    
                    if (!text.isNullOrBlank()) {
                        repository.insertMessage(ChatMsg(role = "assistant", content = text))
                    } else {
                        repository.insertMessage(ChatMsg(role = "assistant", content = "I received an empty response. Let me try again later."))
                    }
                }
            } catch (e: Exception) {
                repository.insertMessage(
                    ChatMsg(
                        role = "assistant",
                        content = "Error calling Gemini: ${e.message}\n\nFallback: ${getSimulatedResponse(question, "")}"
                    )
                )
            } finally {
                _isSending.value = false
            }
        }
    }

    fun submitFeedback(email: String, rating: Int, comment: String) {
        viewModelScope.launch {
            repository.submitFeedback(Feedback(email = email, rating = rating, comment = comment))
        }
    }

    fun scheduleVisit(name: String, email: String, phone: String, date: String, time: String, notes: String) {
        viewModelScope.launch {
            repository.scheduleVisit(CampusVisit(
                parentName = name,
                parentEmail = email,
                parentPhone = phone,
                visitDate = date,
                visitTime = time,
                notes = notes
            ))
        }
    }

    private fun getSimulatedResponse(question: String, context: String): String {
        val q = question.lowercase()
        return when {
            "fee" in q || "cost" in q -> {
                "**Greenwood School Term Fee Structure (2026-2027)**:\n\n" +
                "- **Kindergarten**: $28,000 Tuition + $3,000 Activity + $5,000 Caution Deposit.\n" +
                "- **Grade 1**: $35,000 Tuition + $5,000 Activity + $10,000 Caution Deposit.\n" +
                "- **Grade 5**: $42,000 Tuition + $6,000 Activity + $10,000 Caution Deposit.\n\n" +
                "*(Note: Paid termly, with 3 terms per year. Sibling discount of 10% on tuition fee is available.)*"
            }
            "process" in q || "how to apply" in q -> {
                "**The Admission Process consists of 4 distinct phases**:\n\n" +
                "1. **Online Application**: Register on our web portal.\n" +
                "2. **Document Verification**: Submit birth certificates, transcripts, and photos.\n" +
                "3. **Interactive Session**: Kindergarten play interview or Grade 1+ assessments.\n" +
                "4. **Seat Confirmation**: Complete term fee payment.\n\n" +
                "The last date to register is **August 15, 2026**."
            }
            "transport" in q || "bus" in q -> {
                "**Available Bus Routes**:\n\n" +
                "- **Route A (Downtown)**: $4,500/term. Coverage: Central Station, City Center.\n" +
                "- **Route B (Highlands)**: $5,500/term. Coverage: Highland Hills, Valley View.\n" +
                "- **Route C (Eastside)**: $5,000/term. Status: Limited seats.\n" +
                "*(All vehicles feature active GPS tracking and RFID student checkpoints.)*"
            }
            else -> {
                "Thank you for contacting the Greenwood School admissions desk! " +
                "We provide premium inquiry assistance. Our teacher-to-student ratio is 1:15 in KG and 1:24 in Primary. " +
                "If you would like to schedule a campus visit or provide feedback, please use the navigation tabs above."
            }
        }
    }
}
