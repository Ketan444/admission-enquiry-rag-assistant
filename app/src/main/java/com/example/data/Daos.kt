package com.example.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface ChatDao {
    @Query("SELECT * FROM local_chats ORDER BY timestamp ASC")
    fun getAllChatsFlow(): Flow<List<ChatMsg>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessage(msg: ChatMsg)

    @Query("DELETE FROM local_chats")
    suspend fun clearHistory()
}

@Dao
interface FeeDao {
    @Query("SELECT * FROM local_fees")
    suspend fun getAllFees(): List<FeeStructure>

    @Query("SELECT * FROM local_fees WHERE grade LIKE '%' || :query || '%'")
    suspend fun searchFees(query: String): List<FeeStructure>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFees(fees: List<FeeStructure>)
}

@Dao
interface RouteDao {
    @Query("SELECT * FROM local_routes")
    suspend fun getAllRoutes(): List<BusRoute>

    @Query("SELECT * FROM local_routes WHERE coverageAreas LIKE '%' || :query || '%'")
    suspend fun searchRoutes(query: String): List<BusRoute>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRoutes(routes: List<BusRoute>)
}

@Dao
interface FAQDao {
    @Query("SELECT * FROM local_faqs")
    suspend fun getAllFAQs(): List<FAQ>

    @Query("SELECT * FROM local_faqs WHERE question LIKE '%' || :query || '%' OR answer LIKE '%' || :query || '%'")
    suspend fun searchFAQs(query: String): List<FAQ>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFAQs(faqs: List<FAQ>)
}

@Dao
interface VisitDao {
    @Query("SELECT * FROM local_visits ORDER BY id DESC")
    fun getAllVisitsFlow(): Flow<List<CampusVisit>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertVisit(visit: CampusVisit)
}

@Dao
interface FeedbackDao {
    @Query("SELECT * FROM local_feedback ORDER BY timestamp DESC")
    fun getAllFeedbackFlow(): Flow<List<Feedback>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFeedback(feedback: Feedback)
}
