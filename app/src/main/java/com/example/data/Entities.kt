package com.example.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "local_chats")
data class ChatMsg(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val role: String, // "user" or "assistant"
    val content: String,
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "local_fees")
data class FeeStructure(
    @PrimaryKey val grade: String,
    val admissionFee: Double,
    val tuitionFeeTerm: Double,
    val activityFee: Double,
    val cautionDeposit: Double,
    val frequency: String
)

@Entity(tableName = "local_routes")
data class BusRoute(
    @PrimaryKey val routeName: String,
    val coverageAreas: String,
    val driverName: String,
    val driverPhone: String,
    val termFee: Double,
    val status: String
)

@Entity(tableName = "local_visits")
data class CampusVisit(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val parentName: String,
    val parentEmail: String,
    val parentPhone: String,
    val visitDate: String,
    val visitTime: String,
    val notes: String
)

@Entity(tableName = "local_feedback")
data class Feedback(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val email: String,
    val rating: Int,
    val comment: String,
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "local_faqs")
data class FAQ(
    @PrimaryKey val question: String,
    val answer: String,
    val category: String
)
