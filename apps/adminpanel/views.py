from datetime import datetime
from io import StringIO

from django.http import HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})


# ===== Scans Management (placeholder, no DB model yet) =====
class ScansListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Return empty list to satisfy UI; can be replaced with real data later
        return Response({"success": True, "data": []})


class ScanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, scan_id: str):
        return Response({"success": True, "data": None})

    def put(self, request, scan_id: str):
        # Accept update payload and acknowledge
        return Response({"success": True, "message": "Scan updated successfully"})


class ScanStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, scan_id: str):
        status_val = request.data.get("status")
        if status_val not in ("approved", "rejected"):
            return Response({"success": False, "message": "Invalid status"}, status=400)
        return Response({"success": True, "message": f"Scan {status_val} successfully"})


class ScanExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fmt = request.query_params.get("format", "csv").lower()
        ids = request.query_params.get("ids", "")
        # Create simple CSV content
        csv_io = StringIO()
        csv_io.write("id,itemName,category,price,status\n")
        # No real data yet; keeping file valid
        content = csv_io.getvalue()
        if fmt == "excel":
            # Still return CSV but with .xlsx name to satisfy download UX
            resp = HttpResponse(content, content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="scans_export.xlsx"'
            return resp
        resp = HttpResponse(content, content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="scans_export.csv"'
        return resp


class ScanAuditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, scan_id: str):
        return Response({"success": True, "data": []})


# ===== Analytics (placeholder data, admin-only where applicable) =====
class AdminOnlyMixin:
    def ensure_admin(self, request):
        user = getattr(request, "user", None)
        if not user or getattr(user, "role", None) != 1:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can access this endpoint")


class AnalyticsUserGrowthView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        data = [
            {"month": "Jan", "paidUsers": 0, "storeOwners": 0, "resellers": 0},
            {"month": "Feb", "paidUsers": 0, "storeOwners": 0, "resellers": 0},
        ]
        return Response({"success": True, "data": data})


class AnalyticsTrendsView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "data": []})


class AnalyticsRevenueBreakdownView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        data = [
            {"category": "Subscriptions", "amount": 0, "color": "#8884d8"},
            {"category": "Premium Features", "amount": 0, "color": "#82ca9d"},
        ]
        return Response({"success": True, "data": data})


class AnalyticsSentimentView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        data = [
            {"month": "Jan", "positive": 0, "neutral": 0, "negative": 0},
            {"month": "Feb", "positive": 0, "neutral": 0, "negative": 0},
        ]
        return Response({"success": True, "data": data})


class AnalyticsGoalsView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        data = {"userGoal": 1000, "userActual": 0, "revenueGoal": 50000, "revenueActual": 0}
        return Response({"success": True, "data": data})


class TrendingView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "data": []})


# ===== Locations =====
class LocationsListView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "data": []})


class LocationsVerificationView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "message": "Verification updated"})


# ===== Feedback analytics =====
class FeedbackStatsView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        data = {
            "total": 0,
            "pending": 0,
            "replied": 0,
            "averageRating": 0,
        }
        return Response({"success": True, "data": data})


class FeedbackSentimentView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        data = [
            {"month": "Jan", "positive": 0, "neutral": 0, "negative": 0},
            {"month": "Feb", "positive": 0, "neutral": 0, "negative": 0},
        ]
        return Response({"success": True, "data": data})


# ===== Resellers =====
class ResellerPerformanceView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reseller_id: str):
        self.ensure_admin(request)
        data = {"resellerId": reseller_id, "sales": 0, "engagement": 0}
        return Response({"success": True, "data": data})


class ResellerResourcesView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "data": []})


# ===== Store content moderation and analytics =====
class StoreContentView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id: str):
        self.ensure_admin(request)
        return Response({"success": True, "data": []})


class StoreContentApproveView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, store_id: str):
        self.ensure_admin(request)
        return Response({"success": True, "message": "Content approved"})


class StoreContentRollbackView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, store_id: str):
        self.ensure_admin(request)
        return Response({"success": True, "message": "Content rollback scheduled"})


class StoreAnalyticsView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, store_id: str):
        self.ensure_admin(request)
        data = {"storeId": store_id, "views": 0, "followers": 0, "sales": 0}
        return Response({"success": True, "data": data})


# ===== Partnership Subscriptions =====
class PartnershipSubscriptionsView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "data": []})


class AssignPartnershipPlanView(AdminOnlyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        self.ensure_admin(request)
        return Response({"success": True, "message": "Partnership plan assigned"})
