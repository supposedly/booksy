import { Component } from '@angular/core';
import { FormModule } from '@angular/forms';

import { MemberAuthService } from '../member-auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  uID: string;
  password: string;
  
  constructor(
  private builder: FormBuilder,
  private memberAuthService: MemberAuthService,
  private router: Router
  ) { }

  ngOnInit() {
  }

}
