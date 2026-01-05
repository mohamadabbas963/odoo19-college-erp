/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { onWillStart } from "@odoo/owl";

export class StudentDashboardController extends KanbanController {
    setup() {
        super.setup();
        this.orm = useService("orm");

        // قبل بدء تحميل الواجهة، نذهب للبايثون ونجلب الأرقام
        onWillStart(async () => {
            this.stats = await this.orm.call(
                "college.student",
                "get_student_dashboard_stats",
                []
            );
        });
    }
}

// تسجيل المكون الجديد ليرتبط بالـ js_class="student_dashboard_kanban"
registry.category("views").add("student_dashboard_kanban", {
    ...kanbanView,
    Controller: StudentDashboardController,
    buttonTemplate: "college_erp.StudentDashboardHeader",
});