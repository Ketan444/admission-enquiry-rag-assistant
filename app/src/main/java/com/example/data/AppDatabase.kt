package com.example.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Database(
    entities = [ChatMsg::class, FeeStructure::class, BusRoute::class, CampusVisit::class, Feedback::class, FAQ::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun chatDao(): ChatDao
    abstract fun feeDao(): FeeDao
    abstract fun routeDao(): RouteDao
    abstract fun faqDao(): FAQDao
    abstract fun visitDao(): VisitDao
    abstract fun feedbackDao(): FeedbackDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "admission_assistant_db"
                )
                .addCallback(object : RoomDatabase.Callback() {
                    override fun onCreate(db: SupportSQLiteDatabase) {
                        super.onCreate(db)
                        // Seed tables in a background dispatcher thread
                        CoroutineScope(Dispatchers.IO).launch {
                            val database = getDatabase(context)
                            seedStaticData(database)
                        }
                    }
                })
                .build()
                INSTANCE = instance
                instance
            }
        }

        private suspend fun seedStaticData(db: AppDatabase) {
            // Seeding Fee Table
            db.feeDao().insertFees(
                listOf(
                    FeeStructure("Nursery", 5000.0, 25000.0, 3000.0, 5000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Kindergarten (KG)", 5000.0, 28000.0, 3000.0, 5000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 1", 10000.0, 35000.0, 5000.0, 10000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 2", 10000.0, 35000.0, 5000.0, 10000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 3", 10000.0, 38000.0, 5000.0, 10000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 4", 10000.0, 38000.0, 5000.0, 10000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 5", 10000.0, 42000.0, 6000.0, 10000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 6", 15000.0, 48000.0, 6000.0, 10000.0, "Per Term (3 Terms/Year)"),
                    FeeStructure("Grade 10", 20000.0, 55000.0, 8000.0, 15000.0, "Per Term (3 Terms/Year)")
                )
            )

            // Seeding Bus Route Table
            db.routeDao().insertRoutes(
                listOf(
                    BusRoute("Route A (Downtown)", "Central Station, City Center, North Plaza, Metro Mall", "John Doe", "+1-555-0199", 4500.0, "Available"),
                    BusRoute("Route B (Highlands)", "Highland Hills, Valley View, Crestwood Estates, Oakridge", "Robert Smith", "+1-555-0188", 5500.0, "Available"),
                    BusRoute("Route C (Eastside)", "East Gate, Riverside, Harbour View, Coastal Road", "David Wilson", "+1-555-0177", 5000.0, "Limited"),
                    BusRoute("Route D (West End)", "West Ridge, Sunset Boulevard, Green Meadows, Airport Road", "Michael Brown", "+1-555-0166", 6000.0, "Full")
                )
            )

            // Seeding FAQ Table
            db.faqDao().insertFAQs(
                listOf(
                    FAQ("What is the admission process?", "Greenwood International School follows a structured 4-step admission process:\n1. Online Application: Submit forms via the website.\n2. Document Verification: Auditors review credentials.\n3. Evaluation Session: Assessment test or play interview.\n4. Fees Payment: Secure enrollment.", "Admissions"),
                    FAQ("What is the teacher-to-student ratio?", "Our teacher-to-student ratio is 1:15 in Kindergarten and 1:24 for Grades 1 through 10, ensuring personalized guidance for every child.", "General"),
                    FAQ("Are extracurricular activities included?", "Standard co-curricular activities like music, fine arts, and physical education are included. Special clubs such as Robotics, Horse Riding, and Advanced Tennis have a nominal additional club fee.", "Extracurricular"),
                    FAQ("Does the school offer hostel or boarding?", "No, our school is currently a day school only. We do not provide hostel or residential boarding facilities.", "Facilities"),
                    FAQ("How is safety managed on campus?", "We have 24/7 CCTV surveillance across all corridors and gates, mandatory RFID tracking for students, and highly trained security guards stationed at all entries.", "Safety"),
                    FAQ("Is there a sibling discount on fees?", "Yes, we offer a 10% sibling discount on the Tuition Fee for the second/youngest child currently enrolled in the school.", "Fees")
                )
            )
        }
    }
}
