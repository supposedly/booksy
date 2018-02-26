import { Component, OnInit } from '@angular/core';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-personal-info',
  templateUrl: './personal-info.component.html',
  styles: ['.bad { border-color: #ff2929; color: #ff2929; background-color: #fef0ed; }']
})
export class PersonalInfoComponent {
  msg: string = '';
  fullName: string = '';
  curpass: string = '';
  newpass: string = '';
  conf: string = '';

  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) { this.fullName = globals.name }

  submit() {
    this.memberService.editSelf(this.fullName, this.newpass, this.curpass)
      .subscribe(resp => this.msg = "Edited successfully.", err => this.msg = err.error?err.error:"Error.");
  }

}
