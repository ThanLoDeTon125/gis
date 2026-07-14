import { Module } from "@nestjs/common";
import { HealthModule } from "./health/health.module";
import { DbModule } from "./db/db.module";
import { AuthModule } from "./auth/auth.module";
import { AbilitiesModule } from "./abilities/abilities.module";

@Module({
  imports: [HealthModule, DbModule, AuthModule, AbilitiesModule],
})
export class AppModule {}
