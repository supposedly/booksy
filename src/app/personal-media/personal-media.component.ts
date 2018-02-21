import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-personal-media',
  templateUrl: './personal-media.component.html',
  styleUrls: ['./personal-media.component.css']
})
export class PersonalMediaComponent implements OnInit {
  msg: string = '';
  items: any[] = [];
  cont: number = 0;
  
  constructor(
    public globals: Globals,
    private memberService: MemberService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    let uID = this.route.snapshot.paramMap.get('uID');
    this.getItems(uID || this.globals.uID);
  }
  
  getItems(uID) {
    this.memberService.getItems(uID)
      .subscribe(resp => this.items = resp, err => this.msg = err.error?err.error:'Error.')
  }

}
