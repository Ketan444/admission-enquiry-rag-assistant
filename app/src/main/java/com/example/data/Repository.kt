package com.example.data

import kotlinx.coroutines.flow.Flow
import java.util.Locale

class SchoolRepository(private val db: AppDatabase) {

    val chatHistory: Flow<List<ChatMsg>> = db.chatDao().getAllChatsFlow()
    val visits: Flow<List<CampusVisit>> = db.visitDao().getAllVisitsFlow()
    val feedbackList: Flow<List<Feedback>> = db.feedbackDao().getAllFeedbackFlow()

    suspend fun insertMessage(msg: ChatMsg) {
        db.chatDao().insertMessage(msg)
    }

    suspend fun clearChatHistory() {
        db.chatDao().clearHistory()
    }

    suspend fun scheduleVisit(visit: CampusVisit) {
        db.visitDao().insertVisit(visit)
    }

    suspend fun submitFeedback(feedback: Feedback) {
        db.feedbackDao().insertFeedback(feedback)
    }

    suspend fun getFeesList(): List<FeeStructure> = db.feeDao().getAllFees()
    suspend fun getRoutesList(): List<BusRoute> = db.routeDao().getAllRoutes()
    suspend fun getFAQsList(): List<FAQ> = db.faqDao().getAllFAQs()

    /**
     * Local contextual retriever (hybrid search)
     * Compiles structured data match blocks for local context injection.
     */
    suspend fun retrieveLocalContext(query: String): String {
        val q = query.lowercase(Locale.ROOT).trim()
        val contextBuilder = StringBuilder()

        // 1. Check FAQs
        val matchedFaqs = db.faqDao().searchFAQs(q)
        if (matchedFaqs.isNotEmpty()) {
            contextBuilder.append("--- RELEVANT FREQUENTLY ASKED QUESTIONS ---\n")
            matchedFaqs.forEach {
                contextBuilder.append("Q: ${it.question}\nA: ${it.answer}\n\n")
            }
        } else if (q.contains("process") || q.contains("apply") || q.contains("step")) {
            val faqs = db.faqDao().searchFAQs("process")
            if (faqs.isNotEmpty()) {
                contextBuilder.append("--- RELEVANT FREQUENTLY ASKED QUESTIONS ---\n")
                faqs.forEach { contextBuilder.append("Q: ${it.question}\nA: ${it.answer}\n\n") }
            }
        }

        // 2. Check Fees
        val matchedFees = db.feeDao().searchFees(q)
        if (matchedFees.isNotEmpty()) {
            contextBuilder.append("--- SCHOOL FEE STRUCTURES ---\n")
            matchedFees.forEach {
                contextBuilder.append("Grade: ${it.grade}\n")
                contextBuilder.append("One-time Admission Fee: ${it.admissionFee} USD\n")
                contextBuilder.append("Tuition Fee: ${it.tuitionFeeTerm} USD (Per Term)\n")
                contextBuilder.append("Activity Fee: ${it.activityFee} USD (Per Term)\n")
                contextBuilder.append("Caution Deposit (Refundable): ${it.cautionDeposit} USD\n")
                contextBuilder.append("Frequency: ${it.frequency}\n\n")
            }
        } else if (q.contains("fee") || q.contains("cost") || q.contains("charge") || q.contains("pay")) {
            // Include general fee policy info
            val allFees = db.feeDao().getAllFees()
            contextBuilder.append("--- SCHOOL FEE STRUCTURES ---\n")
            allFees.take(4).forEach {
                contextBuilder.append("Grade: ${it.grade} -> Tuition: ${it.tuitionFeeTerm} USD/Term, Activity: ${it.activityFee} USD/Term\n")
            }
            contextBuilder.append("\n")
        }

        // 3. Check Transport Routes
        val matchedRoutes = db.routeDao().searchRoutes(q)
        if (matchedRoutes.isNotEmpty()) {
            contextBuilder.append("--- BUS TRANSPORT ROUTES ---\n")
            matchedRoutes.forEach {
                contextBuilder.append("Route: ${it.routeName}\n")
                contextBuilder.append("Coverage Areas: ${it.coverageAreas}\n")
                contextBuilder.append("Driver: ${it.driverName} (${it.driverPhone})\n")
                contextBuilder.append("Term Fee: ${it.termFee} USD\n")
                contextBuilder.append("Status: ${it.status}\n\n")
            }
        } else if (q.contains("route") || q.contains("bus") || q.contains("transport") || q.contains("driver")) {
            val allRoutes = db.routeDao().getAllRoutes()
            contextBuilder.append("--- BUS TRANSPORT ROUTES ---\n")
            allRoutes.forEach {
                contextBuilder.append("Route: ${it.routeName} -> Areas: ${it.coverageAreas}, Fee: ${it.termFee} USD, Status: ${it.status}\n")
            }
            contextBuilder.append("\n")
        }

        return contextBuilder.toString()
    }
}
